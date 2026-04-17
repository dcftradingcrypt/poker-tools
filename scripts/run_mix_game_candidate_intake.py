#!/usr/bin/env python3
"""Run blocked-family candidate intake as one validation and promotion dossier."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


INTAKE_DOSSIER_VERSION = "1.0"

COVERAGE_LIMITS = [
    "Synthetic shape-only fixtures can exercise family_shape_match_missing_grounding_evidence without creating source evidence.",
    "promotion_candidate_pending_human_review remains unexercised unless a real provenance-complete blocked-family candidate is staged.",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_repo_path(path_arg: str, repo_root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return repo_root / path


def parse_stdout_json(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: stdout: line={exc.lineno} col={exc.colno} msg={exc.msg}"
    if not isinstance(payload, dict):
        return None, "stdout_json_root_not_object"
    return payload, None


def run_json_command(
    args: list[str],
    *,
    repo_root: Path,
    input_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    input_text = None
    if input_payload is not None:
        input_text = json.dumps(input_payload, indent=2, sort_keys=True) + "\n"
    completed = subprocess.run(
        args,
        cwd=repo_root,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout_json, stdout_json_error = parse_stdout_json(completed.stdout)
    return {
        "command": args,
        "exitCode": completed.returncode,
        "stdoutJson": stdout_json,
        "stdoutJsonError": stdout_json_error,
        "stderr": completed.stderr.strip(),
    }


def load_batch_spec(path_arg: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str]:
    if path_arg == "-":
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            return None, [{"scope": "batch_spec", "message": f"json_decode_error: <stdin>: line={exc.lineno} col={exc.colno} msg={exc.msg}"}], "<stdin>"
        if not isinstance(payload, dict):
            return None, [{"scope": "batch_spec", "message": "root_not_object: <stdin>"}], "<stdin>"
        return payload, [], "<stdin>"

    path = Path(path_arg)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [{"scope": "batch_spec", "message": f"file_not_found: {path}"}], str(path)
    except json.JSONDecodeError as exc:
        return None, [{"scope": "batch_spec", "message": f"json_decode_error: {path}: line={exc.lineno} col={exc.colno} msg={exc.msg}"}], str(path)
    if not isinstance(payload, dict):
        return None, [{"scope": "batch_spec", "message": f"root_not_object: {path}"}], str(path)
    return payload, [], str(path)


def normalize_command_errors(stage: str, run: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if run["exitCode"] != 0:
        errors.append(
            {
                "scope": stage,
                "message": f"command_exit_code={run['exitCode']}",
                "command": run["command"],
            }
        )
    if run.get("stdoutJsonError"):
        errors.append(
            {
                "scope": stage,
                "message": run["stdoutJsonError"],
                "command": run["command"],
            }
        )
    if run.get("stderr"):
        errors.append(
            {
                "scope": stage,
                "message": run["stderr"],
                "command": run["command"],
            }
        )
    payload = run.get("stdoutJson")
    if isinstance(payload, dict):
        for key in ("errors", "executionErrors"):
            values = payload.get(key)
            if isinstance(values, list):
                for value in values:
                    errors.append({"scope": stage, "message": value})
    return errors


def build_batch_spec_from_staging(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    batch_id: str | None,
) -> tuple[dict[str, Any] | None, str, list[dict[str, Any]], dict[str, Any]]:
    command = [
        sys.executable,
        "scripts/build_mix_game_candidate_batch_spec.py",
        "--staging-root",
        str(staging_root),
        "--registry",
        str(registry_path),
    ]
    if batch_id:
        command.extend(["--batch-id", batch_id])
    run = run_json_command(command, repo_root=repo_root)
    payload = run.get("stdoutJson")
    errors = normalize_command_errors("batch_spec_builder", run)
    if not isinstance(payload, dict) or payload.get("status") == "error" or errors:
        return None, "<generated-from-staging-root>", errors, run
    return payload, "<generated-from-staging-root>", [], run


def indexed_by_candidate(records: list[Any], id_key: str = "candidateId") -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        candidate_id = str(record.get(id_key, ""))
        family_id = str(record.get("familyId", ""))
        if candidate_id or family_id:
            out[(candidate_id, family_id)] = record
    return out


def summarize_errors(*error_groups: list[Any]) -> list[Any]:
    errors: list[Any] = []
    for group in error_groups:
        errors.extend(group)
    return errors


def merge_candidate_records(
    *,
    batch_payload: dict[str, Any] | None,
    review_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    batch_results = []
    reviews = []
    if isinstance(batch_payload, dict):
        batch_results = batch_payload.get("results", [])
    if isinstance(review_payload, dict):
        reviews = review_payload.get("reviews", [])
    batch_by_key = indexed_by_candidate(batch_results)
    review_by_key = indexed_by_candidate(reviews)
    keys = sorted(set(batch_by_key) | set(review_by_key))

    candidates: list[dict[str, Any]] = []
    for key in keys:
        batch_result = batch_by_key.get(key, {})
        review = review_by_key.get(key, {})
        notes = []
        for source in (batch_result, review, review.get("batchResult") if isinstance(review, dict) else None):
            if isinstance(source, dict) and isinstance(source.get("notes"), str) and source["notes"]:
                notes.append(source["notes"])
        candidates.append(
            {
                "candidateId": review.get("candidateId") or batch_result.get("candidateId"),
                "familyId": review.get("familyId") or batch_result.get("familyId"),
                "packPath": review.get("packPath") or batch_result.get("packPath"),
                "manifestPath": review.get("manifestPath") or batch_result.get("manifestPath"),
                "validatorVerdict": review.get("validatorVerdict") or batch_result.get("verdict"),
                "reviewVerdict": review.get("reviewVerdict"),
                "currentRepoStatus": review.get("currentRegistryStatus"),
                "expectedValidatorVerdict": review.get("expectedValidatorVerdict") or batch_result.get("expectedVerdict"),
                "expectedValidatorVerdictMatched": batch_result.get("expectedVerdictMatched"),
                "satisfiedPromotionChecks": review.get("satisfiedPromotionChecks", []),
                "missingPromotionChecks": review.get("missingPromotionChecks", []),
                "statusBlockers": review.get("statusBlockers", []),
                "nextRequiredEvidence": review.get("nextRequiredEvidence", []),
                "provenanceGaps": review.get("provenanceGaps", []),
                "excludedAssumptionCollisions": review.get("excludedAssumptionCollisions", []),
                "wrongFamilyMarkers": review.get("wrongFamilyMarkers", []),
                "missingMarkers": review.get("missingMarkers", {}),
                "validationIssueCounts": batch_result.get("issueCounts", {}),
                "executionErrors": summarize_errors(
                    batch_result.get("executionErrors", []) if isinstance(batch_result, dict) else [],
                    review.get("executionErrors", []) if isinstance(review, dict) else [],
                ),
                "notes": sorted(set(notes)),
            }
        )
    return candidates


def count_by_key(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter = Counter(str(record.get(key)) for record in records if record.get(key) is not None)
    return dict(sorted(counter.items()))


def build_summary(
    *,
    candidates: list[dict[str, Any]],
    execution_errors: list[Any],
    review_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    by_review = count_by_key(candidates, "reviewVerdict")
    promotion_candidate_count = by_review.get("promotion_candidate_pending_human_review", 0)
    review_summary = review_payload.get("summary", {}) if isinstance(review_payload, dict) else {}
    false_positive_risk_count = review_summary.get("falsePositiveRiskCount", promotion_candidate_count)
    return {
        "totalCandidates": len(candidates),
        "byValidatorVerdict": count_by_key(candidates, "validatorVerdict"),
        "byReviewVerdict": by_review,
        "executionErrorCount": len(execution_errors) + sum(len(candidate.get("executionErrors", [])) for candidate in candidates),
        "falsePositiveRiskCount": false_positive_risk_count,
        "promotionCandidatePendingHumanReviewCount": promotion_candidate_count,
        "nonPromotableCount": sum(
            1
            for candidate in candidates
            if isinstance(candidate.get("reviewVerdict"), str)
            and candidate["reviewVerdict"].startswith(("non_promotable_", "family_shape_match_missing_grounding_evidence"))
        ),
    }


def build_failure_dossier(
    *,
    input_mode: str,
    registry_path: Path,
    batch_spec_path: str | None,
    execution_errors: list[Any],
    batch_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "intakeDossierVersion": INTAKE_DOSSIER_VERSION,
        "inputMode": input_mode,
        "registryPath": str(registry_path),
        "batchSpecPath": batch_spec_path,
        "batchId": batch_spec.get("batchId") if isinstance(batch_spec, dict) else None,
        "pathBase": batch_spec.get("pathBase") if isinstance(batch_spec, dict) else None,
        "status": "failed",
        "currentGroundingBoundary": {},
        "batchValidationSummary": {},
        "promotionReviewSummary": {},
        "executionErrors": execution_errors,
        "coverageLimits": COVERAGE_LIMITS,
        "summary": {
            "totalCandidates": len(batch_spec.get("candidates", [])) if isinstance(batch_spec, dict) and isinstance(batch_spec.get("candidates"), list) else 0,
            "byValidatorVerdict": {},
            "byReviewVerdict": {},
            "executionErrorCount": len(execution_errors),
            "falsePositiveRiskCount": 0,
            "promotionCandidatePendingHumanReviewCount": 0,
            "nonPromotableCount": 0,
        },
        "candidates": [],
    }


def build_dossier(
    *,
    input_mode: str,
    registry_path: Path,
    batch_spec_path: str,
    batch_spec: dict[str, Any],
    batch_run: dict[str, Any],
    review_run: dict[str, Any],
    setup_errors: list[Any],
    staging_root: Path | None = None,
) -> dict[str, Any]:
    batch_payload = batch_run.get("stdoutJson") if isinstance(batch_run.get("stdoutJson"), dict) else None
    review_payload = review_run.get("stdoutJson") if isinstance(review_run.get("stdoutJson"), dict) else None
    downstream_errors = summarize_errors(
        normalize_command_errors("batch_validation", batch_run),
        normalize_command_errors("promotion_review", review_run),
    )
    execution_errors = setup_errors + downstream_errors
    candidates = merge_candidate_records(batch_payload=batch_payload, review_payload=review_payload)
    summary = build_summary(candidates=candidates, execution_errors=execution_errors, review_payload=review_payload)
    batch_status = batch_payload.get("status") if isinstance(batch_payload, dict) else None
    review_status = review_payload.get("status") if isinstance(review_payload, dict) else None
    status = "ok"
    if execution_errors or batch_status not in {"ok", "completed_with_expected_verdict_mismatches"} or review_status != "ok":
        status = "completed_with_errors"

    dossier: dict[str, Any] = {
        "intakeDossierVersion": INTAKE_DOSSIER_VERSION,
        "inputMode": input_mode,
        "registryPath": str(registry_path),
        "batchSpecPath": batch_spec_path,
        "batchId": batch_spec.get("batchId"),
        "pathBase": batch_spec.get("pathBase"),
        "status": status,
        "currentGroundingBoundary": review_payload.get("currentGroundingBoundary", {}) if isinstance(review_payload, dict) else {},
        "batchValidationSummary": batch_payload.get("summary", {}) if isinstance(batch_payload, dict) else {},
        "promotionReviewSummary": review_payload.get("summary", {}) if isinstance(review_payload, dict) else {},
        "executionErrors": execution_errors,
        "coverageLimits": COVERAGE_LIMITS,
        "summary": summary,
        "candidates": candidates,
    }
    if staging_root is not None:
        dossier["stagingRoot"] = str(staging_root)
    return dossier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-root", help="Candidate staging root to scan into a batch spec before intake.")
    parser.add_argument("--batch-spec", help="Batch spec JSON path, or '-' to read from stdin.")
    parser.add_argument(
        "--registry",
        default=str(get_repo_root() / "out" / "_codex" / "mix_game_family_contract_registry.json"),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    parser.add_argument("--batch-id", default=None, help="Optional batch id when --staging-root is used.")
    parser.add_argument("--output", default=None, help="Optional output path for the consolidated dossier JSON.")
    return parser.parse_args()


def write_payload(payload: dict[str, Any], output: str | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_repo_path(args.registry, repo_root)
    setup_errors: list[Any] = []
    staging_root = None

    if args.staging_root and args.batch_spec:
        staging_root = resolve_repo_path(args.staging_root, repo_root)
        dossier = build_failure_dossier(
            input_mode="invalid_input_mode",
            registry_path=registry_path,
            batch_spec_path=args.batch_spec,
            execution_errors=[
                {
                    "scope": "input_mode",
                    "message": "mutually_exclusive_input_modes: provide either --staging-root or --batch-spec, not both",
                }
            ],
        )
        dossier["stagingRoot"] = str(staging_root)
        write_payload(dossier, args.output)
        return 1

    if not args.staging_root and not args.batch_spec:
        dossier = build_failure_dossier(
            input_mode="invalid_input_mode",
            registry_path=registry_path,
            batch_spec_path=None,
            execution_errors=[
                {
                    "scope": "input_mode",
                    "message": "missing_input_mode: provide either --staging-root or --batch-spec",
                }
            ],
        )
        write_payload(dossier, args.output)
        return 1

    if args.staging_root:
        input_mode = "staging_root"
        staging_root = resolve_repo_path(args.staging_root, repo_root)
        batch_spec, batch_spec_path, builder_errors, _builder_run = build_batch_spec_from_staging(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=staging_root,
            batch_id=args.batch_id,
        )
        setup_errors.extend(builder_errors)
        if batch_spec is None:
            dossier = build_failure_dossier(
                input_mode=input_mode,
                registry_path=registry_path,
                batch_spec_path=batch_spec_path,
                execution_errors=setup_errors,
            )
            dossier["stagingRoot"] = str(staging_root)
            write_payload(dossier, args.output)
            return 1
    else:
        input_mode = "batch_spec"
        assert args.batch_spec is not None
        batch_spec, batch_errors, batch_spec_path = load_batch_spec(args.batch_spec)
        setup_errors.extend(batch_errors)
        if batch_spec is None:
            dossier = build_failure_dossier(
                input_mode=input_mode,
                registry_path=registry_path,
                batch_spec_path=batch_spec_path,
                execution_errors=setup_errors,
            )
            write_payload(dossier, args.output)
            return 1

    batch_run = run_json_command(
        [
            sys.executable,
            "scripts/validate_mix_game_candidate_batch.py",
            "--batch-spec",
            "-",
            "--registry",
            str(registry_path),
        ],
        repo_root=repo_root,
        input_payload=batch_spec,
    )
    review_run = run_json_command(
        [
            sys.executable,
            "scripts/review_mix_game_candidate_promotion.py",
            "--batch-spec",
            "-",
            "--registry",
            str(registry_path),
        ],
        repo_root=repo_root,
        input_payload=batch_spec,
    )
    dossier = build_dossier(
        input_mode=input_mode,
        registry_path=registry_path,
        batch_spec_path=batch_spec_path,
        batch_spec=batch_spec,
        batch_run=batch_run,
        review_run=review_run,
        setup_errors=setup_errors,
        staging_root=staging_root,
    )
    write_payload(dossier, args.output)
    return 0 if dossier["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
