#!/usr/bin/env python3
"""Run one blocked-family source-drop workflow from staging through intake."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SOURCE_DROP_WORKFLOW_VERSION = "1.0"
DEFAULT_REGISTRY = "out/_codex/mix_game_family_contract_registry.json"

COVERAGE_LIMITS = [
    "Retained-source seeding records copied files and hashes only; it does not create normalized family-shaped source evidence.",
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


def load_json_object(path: Path, label: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{label}_not_found: {path}"
    except json.JSONDecodeError as exc:
        return None, f"{label}_json_decode_error: {path}: line={exc.lineno} col={exc.colno} msg={exc.msg}"
    if not isinstance(payload, dict):
        return None, f"{label}_root_not_object: {path}"
    return payload, None


def load_registry_boundary(registry_path: Path) -> dict[str, Any]:
    registry, error = load_json_object(registry_path, "registry")
    if error or registry is None:
        return {}
    return registry.get("currentGroundingBoundary", {})


def normalize_command_errors(stage: str, run: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if run["exitCode"] != 0:
        errors.append({"scope": stage, "message": f"command_exit_code={run['exitCode']}", "command": run["command"]})
    if run.get("stdoutJsonError"):
        errors.append({"scope": stage, "message": run["stdoutJsonError"], "command": run["command"]})
    if run.get("stderr"):
        errors.append({"scope": stage, "message": run["stderr"], "command": run["command"]})
    payload = run.get("stdoutJson")
    if isinstance(payload, dict):
        for key in ("errors", "executionErrors"):
            values = payload.get(key)
            if isinstance(values, list):
                for value in values:
                    errors.append({"scope": stage, "message": value})
    return errors


def build_error(scope: str, message: str) -> dict[str, Any]:
    return {"scope": scope, "message": message}


def non_promotable_from_review(review_verdict: Any) -> bool:
    return isinstance(review_verdict, str) and review_verdict.startswith(
        ("non_promotable_", "family_shape_match_missing_grounding_evidence")
    )


def extract_target_candidate(intake_dossier: dict[str, Any] | None, candidate_id: str | None, family_id: str | None) -> dict[str, Any] | None:
    if not isinstance(intake_dossier, dict):
        return None
    for candidate in intake_dossier.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        if candidate.get("candidateId") == candidate_id and candidate.get("familyId") == family_id:
            return candidate
    return None


def build_batch_spec_for_candidate(
    *,
    candidate_dir: Path,
    registry_path: Path,
    candidate_id: str,
    family_id: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    metadata_path = candidate_dir / "candidate.json"
    metadata, error = load_json_object(metadata_path, "candidate_metadata")
    if error or metadata is None:
        return None, [build_error("candidate_metadata", error or "unknown_candidate_metadata_error")]

    pack_file = metadata.get("packFile")
    manifest_file = metadata.get("manifestFile")
    errors: list[dict[str, Any]] = []
    if not isinstance(pack_file, str) or not pack_file:
        errors.append(build_error("candidate_metadata", "packFile missing_or_not_nonempty_string"))
    if not isinstance(manifest_file, str) or not manifest_file:
        errors.append(build_error("candidate_metadata", "manifestFile missing_or_not_nonempty_string"))
    if errors:
        return None, errors

    pack_path = candidate_dir / pack_file
    manifest_path = candidate_dir / manifest_file
    if not pack_path.is_file():
        errors.append(build_error("candidate_metadata", f"pack_file_not_found: {pack_path}"))
    if not manifest_path.is_file():
        errors.append(build_error("candidate_metadata", f"manifest_file_not_found: {manifest_path}"))
    if errors:
        return None, errors

    entry: dict[str, Any] = {
        "candidateId": candidate_id,
        "familyId": family_id,
        "packPath": str(pack_path),
        "manifestPath": str(manifest_path),
    }
    expected = metadata.get("expectedVerdict")
    notes = metadata.get("notes")
    if isinstance(expected, str) and expected:
        entry["expectedVerdict"] = expected
    if isinstance(notes, str) and notes:
        entry["notes"] = notes

    batch_spec = {
        "batchSpecVersion": "1.0",
        "batchId": f"source-drop-workflow-{candidate_id}",
        "description": "Generated by source-drop workflow for one target candidate. Success is not family-status promotion.",
        "registryPath": str(registry_path),
        "pathBase": "repo_root",
        "generatedBy": "scripts/run_mix_game_source_drop_workflow.py",
        "candidateEntrySchema": {
            "required": ["candidateId", "familyId", "packPath", "manifestPath"],
            "optional": ["notes", "expectedVerdict"],
        },
        "candidates": [entry],
    }
    return batch_spec, []


def build_summary(
    *,
    status: str,
    source_seed_result: dict[str, Any] | None,
    intake_dossier: dict[str, Any] | None,
    target_candidate: dict[str, Any] | None,
    execution_errors: list[dict[str, Any]],
) -> dict[str, Any]:
    intake_summary = intake_dossier.get("summary", {}) if isinstance(intake_dossier, dict) else {}
    seed_status = source_seed_result.get("status") if isinstance(source_seed_result, dict) else None
    non_grounding = source_seed_result.get("nonGroundingStatus", {}) if isinstance(source_seed_result, dict) else {}
    review_verdict = target_candidate.get("reviewVerdict") if isinstance(target_candidate, dict) else None
    validator_verdict = target_candidate.get("validatorVerdict") if isinstance(target_candidate, dict) else None
    current_statuses = [
        non_grounding.get("currentRepoStatus") if isinstance(non_grounding, dict) else None,
        target_candidate.get("currentRepoStatus") if isinstance(target_candidate, dict) else None,
    ]
    blocked_status_preserved = all(status_value in {None, "blocked_no_source"} for status_value in current_statuses)
    return {
        "status": status,
        "sourceSeedStatus": seed_status,
        "copiedSourceCount": len(source_seed_result.get("copiedSources", [])) if isinstance(source_seed_result, dict) else 0,
        "targetValidatorVerdict": validator_verdict,
        "targetReviewVerdict": review_verdict,
        "targetStillNonPromotable": non_promotable_from_review(review_verdict),
        "currentRepoStatusPreserved": blocked_status_preserved,
        "byValidatorVerdict": intake_summary.get("byValidatorVerdict", {}),
        "byReviewVerdict": intake_summary.get("byReviewVerdict", {}),
        "executionErrorCount": len(execution_errors),
        "intakeExecutionErrorCount": intake_summary.get("executionErrorCount"),
        "falsePositiveRiskCount": intake_summary.get("falsePositiveRiskCount", 0),
        "promotionCandidatePendingHumanReviewCount": intake_summary.get("promotionCandidatePendingHumanReviewCount", 0),
    }


def build_dossier(
    *,
    mode: str | None,
    status: str,
    registry_path: Path,
    candidate_dir: Path | None,
    family_id: str | None,
    candidate_id: str | None,
    scaffold_result: dict[str, Any] | None,
    source_seed_result: dict[str, Any] | None,
    intake_dossier: dict[str, Any] | None,
    generated_batch_spec: dict[str, Any] | None,
    execution_errors: list[dict[str, Any]],
    warnings: list[Any] | None = None,
) -> dict[str, Any]:
    target_candidate = extract_target_candidate(intake_dossier, candidate_id, family_id)
    dossier = {
        "sourceDropWorkflowVersion": SOURCE_DROP_WORKFLOW_VERSION,
        "mode": mode,
        "status": status,
        "registryPath": str(registry_path),
        "currentGroundingBoundary": load_registry_boundary(registry_path),
        "candidateDir": str(candidate_dir) if candidate_dir is not None else None,
        "familyId": family_id,
        "candidateId": candidate_id,
        "scaffoldResult_or_null": scaffold_result,
        "sourceSeedResult": source_seed_result,
        "generatedBatchSpec": generated_batch_spec,
        "intakeDossier": intake_dossier,
        "executionErrors": execution_errors,
        "warnings": warnings or [],
        "coverageLimits": COVERAGE_LIMITS,
        "summary": build_summary(
            status=status,
            source_seed_result=source_seed_result,
            intake_dossier=intake_dossier,
            target_candidate=target_candidate,
            execution_errors=execution_errors,
        ),
    }
    return dossier


def write_payload(payload: dict[str, Any], output: str | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def validate_mode(args: argparse.Namespace) -> tuple[str | None, list[dict[str, Any]]]:
    has_existing = bool(args.candidate_dir)
    scaffold_values = [args.family, args.candidate_id, args.staging_root]
    has_any_scaffold = any(scaffold_values)
    has_all_scaffold = all(scaffold_values)

    if has_existing and has_any_scaffold:
        return None, [
            build_error(
                "mode_selection",
                "conflicting_mode_selection: provide either --candidate-dir or --family plus --candidate-id plus --staging-root",
            )
        ]
    if has_existing:
        return "existing_candidate_dir", []
    if has_all_scaffold:
        return "scaffold_new", []
    if has_any_scaffold:
        return None, [
            build_error(
                "mode_selection",
                "incomplete_scaffold_new_mode: require --family, --candidate-id, and --staging-root together",
            )
        ]
    return None, [
        build_error(
            "mode_selection",
            "missing_mode_selection: provide --candidate-dir or --family plus --candidate-id plus --staging-root",
        )
    ]


def validate_source_files(source_files: list[str], repo_root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    resolved: list[Path] = []
    if not source_files:
        return [], [build_error("source_files", "missing_source_file_input: provide at least one --source-file")]
    for source_file in source_files:
        path = resolve_repo_path(source_file, repo_root)
        resolved.append(path)
        if not path.is_file():
            errors.append(build_error("source_files", f"source_file_not_found_or_not_file: {path}"))
    return resolved, errors


def run_scaffold(
    *,
    args: argparse.Namespace,
    repo_root: Path,
    registry_path: Path,
) -> tuple[Path | None, dict[str, Any] | None, list[dict[str, Any]]]:
    assert args.family is not None
    assert args.candidate_id is not None
    assert args.staging_root is not None
    command = [
        sys.executable,
        "scripts/init_mix_game_candidate_staging.py",
        "--family",
        args.family,
        "--candidate-id",
        args.candidate_id,
        "--out-dir",
        str(resolve_repo_path(args.staging_root, repo_root)),
        "--registry",
        str(registry_path),
        "--expected-verdict",
        "candidate_non_grounding_template_match",
    ]
    for note in args.note:
        command.extend(["--notes", note])
    if not args.note:
        command.extend(["--notes", "Source-drop workflow scaffold; not source evidence."])
    run = run_json_command(command, repo_root=repo_root)
    payload = run.get("stdoutJson") if isinstance(run.get("stdoutJson"), dict) else None
    errors = normalize_command_errors("scaffold", run)
    if not isinstance(payload, dict) or payload.get("status") != "ok" or errors:
        return None, payload, errors
    return Path(payload["candidateDir"]), payload, []


def run_seed(
    *,
    args: argparse.Namespace,
    repo_root: Path,
    registry_path: Path,
    candidate_dir: Path,
    source_files: list[Path],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    command = [
        sys.executable,
        "scripts/seed_mix_game_candidate_sources.py",
        "--candidate-dir",
        str(candidate_dir),
        "--registry",
        str(registry_path),
    ]
    for source_file in source_files:
        command.extend(["--source-file", str(source_file)])
    for source_reference in args.source_reference:
        command.extend(["--source-reference", source_reference])
    if args.retrieved_at:
        command.extend(["--retrieved-at", args.retrieved_at])
    for note in args.note:
        command.extend(["--note", note])
    run = run_json_command(command, repo_root=repo_root)
    payload = run.get("stdoutJson") if isinstance(run.get("stdoutJson"), dict) else None
    errors = normalize_command_errors("source_seed", run)
    if not isinstance(payload, dict) or payload.get("status") != "ok" or errors:
        return payload, errors
    return payload, []


def run_intake_for_candidate(
    *,
    repo_root: Path,
    registry_path: Path,
    candidate_dir: Path,
    candidate_id: str,
    family_id: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    batch_spec, batch_errors = build_batch_spec_for_candidate(
        candidate_dir=candidate_dir,
        registry_path=registry_path,
        candidate_id=candidate_id,
        family_id=family_id,
    )
    if batch_errors or batch_spec is None:
        return None, batch_spec, batch_errors
    run = run_json_command(
        [
            sys.executable,
            "scripts/run_mix_game_candidate_intake.py",
            "--batch-spec",
            "-",
            "--registry",
            str(registry_path),
        ],
        repo_root=repo_root,
        input_payload=batch_spec,
    )
    payload = run.get("stdoutJson") if isinstance(run.get("stdoutJson"), dict) else None
    errors = normalize_command_errors("intake", run)
    if not isinstance(payload, dict) or payload.get("status") != "ok" or errors:
        return payload, batch_spec, errors
    return payload, batch_spec, []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", help="Existing candidate directory to seed and run through intake.")
    parser.add_argument("--family", help="Blocked-family id for scaffold-new mode.")
    parser.add_argument("--candidate-id", help="Candidate id for scaffold-new mode.")
    parser.add_argument("--staging-root", help="Staging root for scaffold-new mode.")
    parser.add_argument("--source-file", action="append", default=[], help="Retained source file to seed. Repeatable.")
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY,
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    parser.add_argument("--source-reference", action="append", default=[], help="Optional shared or per-file source reference.")
    parser.add_argument("--retrieved-at", default=None, help="Optional retrieval timestamp to pass into the seed tool.")
    parser.add_argument("--note", action="append", default=[], help="Optional note to pass into scaffold and seed records.")
    parser.add_argument("--output", default=None, help="Optional path for the workflow dossier JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_repo_path(args.registry, repo_root)
    mode, mode_errors = validate_mode(args)
    source_files, source_errors = validate_source_files(args.source_file, repo_root)
    setup_errors = mode_errors + source_errors
    candidate_dir = resolve_repo_path(args.candidate_dir, repo_root) if args.candidate_dir else None

    if setup_errors:
        dossier = build_dossier(
            mode=mode,
            status="failed",
            registry_path=registry_path,
            candidate_dir=candidate_dir,
            family_id=args.family,
            candidate_id=args.candidate_id,
            scaffold_result=None,
            source_seed_result=None,
            intake_dossier=None,
            generated_batch_spec=None,
            execution_errors=setup_errors,
        )
        write_payload(dossier, args.output)
        return 1

    scaffold_result: dict[str, Any] | None = None
    if mode == "scaffold_new":
        candidate_dir, scaffold_result, scaffold_errors = run_scaffold(args=args, repo_root=repo_root, registry_path=registry_path)
        if scaffold_errors or candidate_dir is None:
            dossier = build_dossier(
                mode=mode,
                status="failed",
                registry_path=registry_path,
                candidate_dir=candidate_dir,
                family_id=args.family,
                candidate_id=args.candidate_id,
                scaffold_result=scaffold_result,
                source_seed_result=None,
                intake_dossier=None,
                generated_batch_spec=None,
                execution_errors=scaffold_errors,
            )
            write_payload(dossier, args.output)
            return 1

    assert candidate_dir is not None
    source_seed_result, seed_errors = run_seed(
        args=args,
        repo_root=repo_root,
        registry_path=registry_path,
        candidate_dir=candidate_dir,
        source_files=source_files,
    )
    seed_family_id = source_seed_result.get("familyId") if isinstance(source_seed_result, dict) else args.family
    seed_candidate_id = source_seed_result.get("candidateId") if isinstance(source_seed_result, dict) else args.candidate_id
    seed_warnings = source_seed_result.get("warnings", []) if isinstance(source_seed_result, dict) else []
    if seed_errors or not isinstance(source_seed_result, dict):
        dossier = build_dossier(
            mode=mode,
            status="failed",
            registry_path=registry_path,
            candidate_dir=candidate_dir,
            family_id=seed_family_id,
            candidate_id=seed_candidate_id,
            scaffold_result=scaffold_result,
            source_seed_result=source_seed_result,
            intake_dossier=None,
            generated_batch_spec=None,
            execution_errors=seed_errors,
            warnings=seed_warnings,
        )
        write_payload(dossier, args.output)
        return 1

    family_id = source_seed_result.get("familyId")
    candidate_id = source_seed_result.get("candidateId")
    if not isinstance(family_id, str) or not isinstance(candidate_id, str):
        errors = [build_error("source_seed", "source_seed_result_missing_familyId_or_candidateId")]
        dossier = build_dossier(
            mode=mode,
            status="failed",
            registry_path=registry_path,
            candidate_dir=candidate_dir,
            family_id=family_id if isinstance(family_id, str) else None,
            candidate_id=candidate_id if isinstance(candidate_id, str) else None,
            scaffold_result=scaffold_result,
            source_seed_result=source_seed_result,
            intake_dossier=None,
            generated_batch_spec=None,
            execution_errors=errors,
            warnings=seed_warnings,
        )
        write_payload(dossier, args.output)
        return 1

    intake_dossier, batch_spec, intake_errors = run_intake_for_candidate(
        repo_root=repo_root,
        registry_path=registry_path,
        candidate_dir=candidate_dir,
        candidate_id=candidate_id,
        family_id=family_id,
    )
    status = "ok" if not intake_errors else "failed"
    dossier = build_dossier(
        mode=mode,
        status=status,
        registry_path=registry_path,
        candidate_dir=candidate_dir,
        family_id=family_id,
        candidate_id=candidate_id,
        scaffold_result=scaffold_result,
        source_seed_result=source_seed_result,
        intake_dossier=intake_dossier,
        generated_batch_spec=batch_spec,
        execution_errors=intake_errors,
        warnings=seed_warnings,
    )
    write_payload(dossier, args.output)
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
