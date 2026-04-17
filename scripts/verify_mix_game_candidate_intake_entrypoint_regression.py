#!/usr/bin/env python3
"""Regression checks for the one-shot blocked-family intake entrypoint."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REGRESSION_VERSION = "1.0"
TEMPLATE_VALIDATOR_VERDICT = "candidate_non_grounding_template_match"
TEMPLATE_REVIEW_VERDICT = "non_promotable_template_placeholder"
SHAPE_ONLY_VALIDATOR_VERDICT = "shape_match_missing_grounding_evidence"
SHAPE_ONLY_REVIEW_VERDICT = "family_shape_match_missing_grounding_evidence"
GROUNDED_VALIDATOR_VERDICT = "rejected_wrong_family_markers"
GROUNDED_REVIEW_VERDICT = "non_promotable_wrong_family"

DOSSIER_REQUIRED_KEYS = {
    "intakeDossierVersion",
    "inputMode",
    "registryPath",
    "batchSpecPath",
    "batchId",
    "pathBase",
    "status",
    "currentGroundingBoundary",
    "batchValidationSummary",
    "promotionReviewSummary",
    "executionErrors",
    "coverageLimits",
    "summary",
    "candidates",
}

CANDIDATE_REQUIRED_KEYS = {
    "candidateId",
    "familyId",
    "packPath",
    "manifestPath",
    "validatorVerdict",
    "reviewVerdict",
    "currentRepoStatus",
    "satisfiedPromotionChecks",
    "missingPromotionChecks",
    "statusBlockers",
    "nextRequiredEvidence",
    "provenanceGaps",
    "excludedAssumptionCollisions",
    "notes",
}

GROUNDED_NEGATIVE_SOURCES = [
    {
        "sourceId": "base_9max",
        "packPath": "out/_private/pushfold_real_data/pack.json",
        "manifestPath": "out/_private/pushfold_real_data/manifest.json",
    },
    {
        "sourceId": "tool_openjam",
        "packPath": "out/_private/pushfold_real_data_regimes/tool10max_bb100_openjam/pack.json",
        "manifestPath": "out/_private/pushfold_real_data_regimes/tool10max_bb100_openjam/manifest.json",
    },
    {
        "sourceId": "tool_call",
        "packPath": "out/_private/pushfold_real_data_regimes/tool10max_bb100_call/pack.json",
        "manifestPath": "out/_private/pushfold_real_data_regimes/tool10max_bb100_call/manifest.json",
    },
]

COVERAGE_LIMITS = [
    "Synthetic shape-only fixtures exercise family_shape_match_missing_grounding_evidence without creating source evidence.",
    "No real provenance-complete candidate exists in the remaining blocked-family set to exercise promotion_candidate_pending_human_review.",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def family_slug(family_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", family_id.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"root_not_object: {path}")
    return payload


def parse_stdout_json(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: stdout: line={exc.lineno} col={exc.colno} msg={exc.msg}"
    if not isinstance(payload, dict):
        return None, "stdout_json_root_not_object"
    return payload, None


def run_command(
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
    stdout_json, stdout_json_error = parse_stdout_json(completed.stdout) if completed.stdout.strip() else (None, None)
    return {
        "command": args,
        "exitCode": completed.returncode,
        "stdout": completed.stdout,
        "stdoutJson": stdout_json,
        "stdoutJsonError": stdout_json_error,
        "stderr": completed.stderr.strip(),
    }


def run_entrypoint(
    *,
    repo_root: Path,
    args: list[str],
    output_path: Path | None = None,
) -> dict[str, Any]:
    command = [sys.executable, "scripts/run_mix_game_candidate_intake.py", *args]
    if output_path is not None:
        command.extend(["--output", str(output_path)])
    run = run_command(command, repo_root=repo_root)
    payload = None
    payload_error = None
    output_exists = output_path.is_file() if output_path is not None else False
    if output_path is not None:
        if output_exists:
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    payload = None
                    payload_error = f"output_json_root_not_object: {output_path}"
            except json.JSONDecodeError as exc:
                payload_error = f"json_decode_error: {output_path}: line={exc.lineno} col={exc.colno} msg={exc.msg}"
        else:
            payload_error = f"output_file_not_written: {output_path}"
    else:
        payload = run.get("stdoutJson")
        payload_error = run.get("stdoutJsonError")
    run.update(
        {
            "payload": payload,
            "payloadError": payload_error,
            "outputPath": str(output_path) if output_path is not None else None,
            "outputFileExists": output_exists,
        }
    )
    return run


def get_family_ids(registry: dict[str, Any]) -> list[str]:
    boundary = registry.get("currentGroundingBoundary", {})
    blocked = boundary.get("blockedFamilies") if isinstance(boundary, dict) else None
    if isinstance(blocked, list) and all(isinstance(family_id, str) and family_id for family_id in blocked):
        return [str(family_id) for family_id in blocked]

    families = registry.get("families")
    if not isinstance(families, list):
        raise ValueError("registry.families missing_or_not_list")
    family_ids = [
        entry.get("familyId")
        for entry in families
        if isinstance(entry, dict) and entry.get("currentRepoStatus") == "blocked_no_source"
    ]
    if not all(isinstance(family_id, str) and family_id for family_id in family_ids):
        raise ValueError("registry.families contains missing blocked familyId")
    return [str(family_id) for family_id in family_ids]


def make_subtest_result(
    *,
    name: str,
    status: str,
    input_mode: str | None = None,
    candidate_count: int = 0,
    expected_count: int = 0,
    execution_error_count: int = 0,
    false_positive_risk_count: int = 0,
    failing_candidate_ids: list[str] | None = None,
    deterministic_errors: list[str] | None = None,
    output_file_verified: bool = False,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "inputMode": input_mode,
        "candidateCount": candidate_count,
        "expectedCount": expected_count,
        "executionErrorCount": execution_error_count,
        "falsePositiveRiskCount": false_positive_risk_count,
        "failingCandidateIds": failing_candidate_ids or [],
        "deterministicErrors": deterministic_errors or [],
        "outputFileVerified": output_file_verified,
        "details": details or {},
    }


def verify_dossier_schema(payload: dict[str, Any], *, expect_staging_root: bool) -> list[str]:
    errors = [f"missing top-level key: {key}" for key in sorted(DOSSIER_REQUIRED_KEYS - set(payload))]
    if expect_staging_root and "stagingRoot" not in payload:
        errors.append("missing top-level key: stagingRoot")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates missing_or_not_list")
        return errors
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"candidate[{index}] root_not_object")
            continue
        for key in sorted(CANDIDATE_REQUIRED_KEYS - set(candidate)):
            errors.append(f"candidate[{index}] missing key: {key}")
    return errors


def summarize_control_failures(
    payload: dict[str, Any],
    *,
    expected_validator_verdict: str,
    expected_review_verdict: str,
) -> list[str]:
    failures: list[str] = []
    for candidate in payload.get("candidates", []):
        if not isinstance(candidate, dict):
            failures.append("<invalid-candidate>")
            continue
        candidate_id = str(candidate.get("candidateId", "<unknown-candidate>"))
        if candidate.get("validatorVerdict") != expected_validator_verdict:
            failures.append(candidate_id)
        if candidate.get("reviewVerdict") != expected_review_verdict:
            failures.append(candidate_id)
        if candidate.get("executionErrors"):
            failures.append(candidate_id)
    return sorted(set(failures))


def count_execution_errors(payload: dict[str, Any] | None) -> int:
    if not isinstance(payload, dict):
        return 1
    summary = payload.get("summary")
    if isinstance(summary, dict):
        value = summary.get("executionErrorCount", 0)
        if isinstance(value, int):
            return value
    errors = payload.get("executionErrors")
    return len(errors) if isinstance(errors, list) else 0


def control_subtest_from_dossier(
    *,
    name: str,
    run: dict[str, Any],
    input_mode: str,
    expected_count: int,
    expected_validator_verdict: str,
    expected_review_verdict: str,
    expect_staging_root: bool,
) -> dict[str, Any]:
    payload = run.get("payload")
    schema_errors = verify_dossier_schema(payload, expect_staging_root=expect_staging_root) if isinstance(payload, dict) else ["payload_not_object"]
    failing_ids = (
        summarize_control_failures(
            payload,
            expected_validator_verdict=expected_validator_verdict,
            expected_review_verdict=expected_review_verdict,
        )
        if isinstance(payload, dict)
        else ["<payload-not-object>"]
    )
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    execution_error_count = count_execution_errors(payload)
    false_positive_risk_count = int(summary.get("falsePositiveRiskCount", 0) or 0) if isinstance(summary, dict) else 0
    by_validator = summary.get("byValidatorVerdict", {}) if isinstance(summary, dict) else {}
    by_review = summary.get("byReviewVerdict", {}) if isinstance(summary, dict) else {}
    passed = (
        run["exitCode"] == 0
        and isinstance(payload, dict)
        and payload.get("status") == "ok"
        and payload.get("inputMode") == input_mode
        and summary.get("totalCandidates") == expected_count
        and by_validator.get(expected_validator_verdict) == expected_count
        and by_review.get(expected_review_verdict) == expected_count
        and execution_error_count == 0
        and false_positive_risk_count == 0
        and not schema_errors
        and not failing_ids
        and run.get("outputFileExists") is True
        and not run.get("payloadError")
    )
    deterministic_errors = list(schema_errors)
    if run.get("payloadError"):
        deterministic_errors.append(str(run["payloadError"]))
    if run.get("stderr"):
        deterministic_errors.append(str(run["stderr"]))
    return make_subtest_result(
        name=name,
        status="passed" if passed else "failed",
        input_mode=input_mode,
        candidate_count=int(summary.get("totalCandidates", 0) or 0) if isinstance(summary, dict) else 0,
        expected_count=expected_count,
        execution_error_count=execution_error_count,
        false_positive_risk_count=false_positive_risk_count,
        failing_candidate_ids=failing_ids,
        deterministic_errors=deterministic_errors,
        output_file_verified=bool(run.get("outputFileExists")) and not schema_errors and not run.get("payloadError"),
        details={
            "exitCode": run["exitCode"],
            "outputPath": run.get("outputPath"),
            "dossierStatus": None if not isinstance(payload, dict) else payload.get("status"),
            "validatorSummary": None if not isinstance(payload, dict) else payload.get("batchValidationSummary", {}),
            "reviewSummary": None if not isinstance(payload, dict) else payload.get("promotionReviewSummary", {}),
        },
    )


def init_shape_only_controls(repo_root: Path, registry_path: Path, staging_root: Path, family_ids: list[str]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for family_id in family_ids:
        runs.append(
            run_command(
                [
                    sys.executable,
                    "scripts/init_mix_game_shape_only_candidates.py",
                    "--family",
                    family_id,
                    "--candidate-id",
                    f"entrypoint_regression_shape_{family_slug(family_id)}",
                    "--out-dir",
                    str(staging_root),
                    "--registry",
                    str(registry_path),
                    "--expected-verdict",
                    SHAPE_ONLY_VALIDATOR_VERDICT,
                    "--notes",
                    "Synthetic shape-only intake entrypoint regression control. It is not source evidence.",
                ],
                repo_root=repo_root,
            )
        )
    return runs


def init_template_candidate(repo_root: Path, registry_path: Path, staging_root: Path, family_id: str, candidate_id: str) -> dict[str, Any]:
    return run_command(
        [
            sys.executable,
            "scripts/init_mix_game_candidate_staging.py",
            "--family",
            family_id,
            "--candidate-id",
            candidate_id,
            "--out-dir",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--expected-verdict",
            TEMPLATE_VALIDATOR_VERDICT,
            "--notes",
            "Malformed staging-root regression fixture; not source evidence.",
        ],
        repo_root=repo_root,
    )


def build_grounded_negative_batch_spec(family_ids: list[str]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for family_id in family_ids:
        for source in GROUNDED_NEGATIVE_SOURCES:
            candidates.append(
                {
                    "candidateId": f"entrypoint_regression_negative_{source['sourceId']}_{family_slug(family_id)}",
                    "familyId": family_id,
                    "packPath": source["packPath"],
                    "manifestPath": source["manifestPath"],
                    "expectedVerdict": GROUNDED_VALIDATOR_VERDICT,
                    "notes": f"Grounded cc_high / 2-card {source['sourceId']} wrong-family negative control against {family_id}.",
                }
            )
    return {
        "batchSpecVersion": "1.0",
        "batchId": "entrypoint-regression-grounded-negative-controls",
        "description": "Grounded cc_high / 2-card real packs used as wrong-family negatives against blocked-family validators.",
        "registryPath": "out/_codex/mix_game_family_contract_registry.json",
        "pathBase": "repo_root",
        "candidateEntrySchema": {
            "required": ["candidateId", "familyId", "packPath", "manifestPath"],
            "optional": ["notes", "expectedVerdict"],
        },
        "candidates": candidates,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_batch_spec_from_staging(repo_root: Path, registry_path: Path, staging_root: Path, batch_id: str) -> dict[str, Any]:
    return run_command(
        [
            sys.executable,
            "scripts/build_mix_game_candidate_batch_spec.py",
            "--staging-root",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--batch-id",
            batch_id,
        ],
        repo_root=repo_root,
    )


def run_template_controls(repo_root: Path, registry_path: Path, temp_root: Path, family_ids: list[str]) -> dict[str, Any]:
    staging_root = temp_root / "template_batch_spec_staging"
    scaffold_errors: list[str] = []
    for family_id in family_ids:
        candidate_id = f"entrypoint_regression_template_{family_slug(family_id)}"
        scaffold_run = init_template_candidate(repo_root, registry_path, staging_root, family_id, candidate_id)
        if scaffold_run["exitCode"] != 0 or not isinstance(scaffold_run.get("stdoutJson"), dict) or scaffold_run["stdoutJson"].get("status") != "ok":
            scaffold_errors.append(f"{candidate_id}: scaffold_failed")

    if scaffold_errors:
        return make_subtest_result(
            name="batch_spec_template_controls",
            status="failed",
            input_mode="batch_spec",
            candidate_count=0,
            expected_count=len(family_ids),
            execution_error_count=len(scaffold_errors),
            deterministic_errors=scaffold_errors,
            output_file_verified=False,
            details={"stagingRoot": str(staging_root)},
        )

    batch_build_run = build_batch_spec_from_staging(
        repo_root,
        registry_path,
        staging_root,
        "entrypoint-regression-template-controls",
    )
    batch_payload = batch_build_run.get("stdoutJson") if isinstance(batch_build_run.get("stdoutJson"), dict) else None
    if batch_build_run["exitCode"] != 0 or not isinstance(batch_payload, dict):
        return make_subtest_result(
            name="batch_spec_template_controls",
            status="failed",
            input_mode="batch_spec",
            candidate_count=0,
            expected_count=len(family_ids),
            execution_error_count=1,
            deterministic_errors=[batch_build_run.get("stderr") or batch_build_run.get("stdoutJsonError") or "batch_spec_build_failed"],
            output_file_verified=False,
            details={"stagingRoot": str(staging_root)},
        )

    batch_spec_path = temp_root / "entrypoint_template_controls_batch.json"
    write_json(batch_spec_path, batch_payload)
    output_path = temp_root / "template_entrypoint_dossier.json"
    run = run_entrypoint(
        repo_root=repo_root,
        args=[
            "--batch-spec",
            str(batch_spec_path),
            "--registry",
            str(registry_path),
        ],
        output_path=output_path,
    )
    return control_subtest_from_dossier(
        name="batch_spec_template_controls",
        run=run,
        input_mode="batch_spec",
        expected_count=len(family_ids),
        expected_validator_verdict=TEMPLATE_VALIDATOR_VERDICT,
        expected_review_verdict=TEMPLATE_REVIEW_VERDICT,
        expect_staging_root=False,
    )


def run_shape_only_controls(repo_root: Path, registry_path: Path, temp_root: Path, family_ids: list[str]) -> dict[str, Any]:
    staging_root = temp_root / "shape_only_staging"
    fixture_runs = init_shape_only_controls(repo_root, registry_path, staging_root, family_ids)
    fixture_errors = [
        str(run.get("stderr") or run.get("stdoutJsonError") or run.get("stdout") or "shape_only_fixture_failed")
        for run in fixture_runs
        if run["exitCode"] != 0 or not isinstance(run.get("stdoutJson"), dict) or run["stdoutJson"].get("status") != "ok"
    ]
    if fixture_errors:
        return make_subtest_result(
            name="staging_root_shape_only_controls",
            status="failed",
            input_mode="staging_root",
            candidate_count=0,
            expected_count=len(family_ids),
            execution_error_count=len(fixture_errors),
            deterministic_errors=fixture_errors,
            details={"stagingRoot": str(staging_root)},
        )

    output_path = temp_root / "shape_only_entrypoint_dossier.json"
    run = run_entrypoint(
        repo_root=repo_root,
        args=[
            "--staging-root",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--batch-id",
            "entrypoint-regression-shape-only-controls",
        ],
        output_path=output_path,
    )
    return control_subtest_from_dossier(
        name="staging_root_shape_only_controls",
        run=run,
        input_mode="staging_root",
        expected_count=len(family_ids),
        expected_validator_verdict=SHAPE_ONLY_VALIDATOR_VERDICT,
        expected_review_verdict=SHAPE_ONLY_REVIEW_VERDICT,
        expect_staging_root=True,
    )


def run_grounded_negative_controls(repo_root: Path, registry_path: Path, temp_root: Path, family_ids: list[str]) -> dict[str, Any]:
    batch_spec = build_grounded_negative_batch_spec(family_ids)
    batch_path = temp_root / "grounded_negative_batch.json"
    output_path = temp_root / "grounded_negative_entrypoint_dossier.json"
    write_json(batch_path, batch_spec)
    run = run_entrypoint(
        repo_root=repo_root,
        args=["--batch-spec", str(batch_path), "--registry", str(registry_path)],
        output_path=output_path,
    )
    return control_subtest_from_dossier(
        name="batch_spec_grounded_negative_controls",
        run=run,
        input_mode="batch_spec",
        expected_count=len(family_ids) * len(GROUNDED_NEGATIVE_SOURCES),
        expected_validator_verdict=GROUNDED_VALIDATOR_VERDICT,
        expected_review_verdict=GROUNDED_REVIEW_VERDICT,
        expect_staging_root=False,
    )


def fail_closed_subtest(
    *,
    name: str,
    run: dict[str, Any],
    expected_message: str,
) -> dict[str, Any]:
    payload = run.get("payload")
    errors = payload.get("executionErrors", []) if isinstance(payload, dict) else []
    rendered_errors = [json.dumps(error, sort_keys=True) if isinstance(error, dict) else str(error) for error in errors]
    schema_errors = verify_dossier_schema(payload, expect_staging_root=False) if isinstance(payload, dict) else ["payload_not_object"]
    message_found = any(expected_message in error for error in rendered_errors)
    passed = (
        run["exitCode"] != 0
        and isinstance(payload, dict)
        and payload.get("status") == "failed"
        and message_found
        and not schema_errors
    )
    deterministic_errors = [] if message_found else [f"expected message not found: {expected_message}"]
    deterministic_errors.extend(schema_errors)
    if run.get("payloadError"):
        deterministic_errors.append(str(run["payloadError"]))
    return make_subtest_result(
        name=name,
        status="passed" if passed else "failed",
        input_mode=payload.get("inputMode") if isinstance(payload, dict) else None,
        execution_error_count=len(rendered_errors),
        deterministic_errors=deterministic_errors or rendered_errors,
        details={
            "exitCode": run["exitCode"],
            "dossierStatus": None if not isinstance(payload, dict) else payload.get("status"),
            "expectedMessage": expected_message,
            "observedErrors": rendered_errors,
        },
    )


def run_fail_closed_controls(repo_root: Path, registry_path: Path, temp_root: Path, family_ids: list[str]) -> list[dict[str, Any]]:
    missing_mode_run = run_entrypoint(
        repo_root=repo_root,
        args=["--registry", str(registry_path)],
    )
    both_modes_run = run_entrypoint(
        repo_root=repo_root,
        args=[
            "--batch-spec",
            "out/_codex/mix_game_candidate_batch_spec_template.json",
            "--staging-root",
            str(temp_root / "unused_staging_root"),
            "--registry",
            str(registry_path),
        ],
    )
    invalid_batch_run = run_entrypoint(
        repo_root=repo_root,
        args=[
            "--batch-spec",
            str(temp_root / "missing_batch_spec.json"),
            "--registry",
            str(registry_path),
        ],
    )

    malformed_root = temp_root / "malformed_missing_pack_staging"
    candidate_id = "entrypoint_regression_missing_pack"
    scaffold_run = init_template_candidate(repo_root, registry_path, malformed_root, family_ids[0], candidate_id)
    if scaffold_run["exitCode"] == 0:
        pack_path = malformed_root / family_slug(family_ids[0]) / candidate_id / "pack.json"
        if pack_path.exists():
            pack_path.unlink()
    builder_failure_run = run_entrypoint(
        repo_root=repo_root,
        args=[
            "--staging-root",
            str(malformed_root),
            "--registry",
            str(registry_path),
            "--batch-id",
            "entrypoint-regression-malformed-missing-pack",
        ],
    )

    return [
        fail_closed_subtest(
            name="fail_closed_missing_input_mode",
            run=missing_mode_run,
            expected_message="missing_input_mode",
        ),
        fail_closed_subtest(
            name="fail_closed_both_input_modes",
            run=both_modes_run,
            expected_message="mutually_exclusive_input_modes",
        ),
        fail_closed_subtest(
            name="fail_closed_invalid_batch_spec_path",
            run=invalid_batch_run,
            expected_message="file_not_found",
        ),
        fail_closed_subtest(
            name="fail_closed_staging_root_builder_missing_pack",
            run=builder_failure_run,
            expected_message="missing pack file",
        ),
    ]


def build_summary(subtests: list[dict[str, Any]]) -> dict[str, Any]:
    failing_subtests = [subtest["name"] for subtest in subtests if subtest["status"] != "passed"]
    failing_candidate_ids = sorted(
        {
            candidate_id
            for subtest in subtests
            for candidate_id in subtest.get("failingCandidateIds", [])
        }
    )
    expected_fail_closed_error_count = sum(
        subtest.get("executionErrorCount", 0)
        for subtest in subtests
        if subtest["name"].startswith("fail_closed_")
    )
    unexpected_execution_error_count = sum(
        subtest.get("executionErrorCount", 0)
        for subtest in subtests
        if not subtest["name"].startswith("fail_closed_")
    )
    return {
        "subtestsTotal": len(subtests),
        "subtestsPassed": sum(1 for subtest in subtests if subtest["status"] == "passed"),
        "subtestsFailed": len(failing_subtests),
        "unexpectedExecutionErrorCount": unexpected_execution_error_count,
        "expectedFailClosedErrorCount": expected_fail_closed_error_count,
        "falsePositiveRiskCount": sum(subtest.get("falsePositiveRiskCount", 0) for subtest in subtests),
        "outputFileVerificationPassed": all(
            subtest.get("outputFileVerified")
            for subtest in subtests
            if subtest["name"] in {"batch_spec_template_controls", "staging_root_shape_only_controls"}
        ),
        "failingSubtests": failing_subtests,
        "failingCandidateIds": failing_candidate_ids,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=str(get_repo_root() / "out" / "_codex" / "mix_game_family_contract_registry.json"),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    registry = load_json_object(registry_path)
    family_ids = get_family_ids(registry)
    if not family_ids:
        payload = {
            "entrypointRegressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "passed",
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "familyIds": [],
            "entrypointDossierRequiredKeys": sorted(DOSSIER_REQUIRED_KEYS),
            "candidateRecordRequiredKeys": sorted(CANDIDATE_REQUIRED_KEYS),
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so blocked-family intake entrypoint regression is not exercised in this pass."
            ],
            "toolsReused": [
                "scripts/run_mix_game_candidate_intake.py",
                "scripts/build_mix_game_candidate_batch_spec.py",
                "scripts/validate_mix_game_candidate_batch.py",
                "scripts/review_mix_game_candidate_promotion.py",
                "scripts/init_mix_game_candidate_staging.py",
                "scripts/init_mix_game_shape_only_candidates.py",
            ],
            "existingScriptsExtended": ["scripts/run_mix_game_candidate_intake.py"],
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "unexpectedExecutionErrorCount": 0,
                "expectedFailClosedErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "outputFileVerificationPassed": True,
                "failingSubtests": [],
                "failingCandidateIds": [],
            },
            "subtests": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    temp_root = Path(tempfile.mkdtemp(prefix="popker_entrypoint_regression_"))

    subtests = [
        run_template_controls(repo_root, registry_path, temp_root, family_ids),
        run_shape_only_controls(repo_root, registry_path, temp_root, family_ids),
        run_grounded_negative_controls(repo_root, registry_path, temp_root, family_ids),
    ]
    subtests.extend(run_fail_closed_controls(repo_root, registry_path, temp_root, family_ids))
    summary = build_summary(subtests)
    status = "passed" if summary["subtestsFailed"] == 0 else "failed"

    payload = {
        "entrypointRegressionVersion": REGRESSION_VERSION,
        "repoRoot": str(repo_root),
        "registryPath": str(registry_path),
        "status": status,
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "familyIds": family_ids,
        "entrypointDossierRequiredKeys": sorted(DOSSIER_REQUIRED_KEYS),
        "candidateRecordRequiredKeys": sorted(CANDIDATE_REQUIRED_KEYS),
        "coverageLimits": COVERAGE_LIMITS,
        "toolsReused": [
            "scripts/run_mix_game_candidate_intake.py",
            "scripts/build_mix_game_candidate_batch_spec.py",
            "scripts/validate_mix_game_candidate_batch.py",
            "scripts/review_mix_game_candidate_promotion.py",
            "scripts/init_mix_game_candidate_staging.py",
            "scripts/init_mix_game_shape_only_candidates.py",
        ],
        "existingScriptsExtended": ["scripts/run_mix_game_candidate_intake.py"],
        "summary": summary,
        "subtests": subtests,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
