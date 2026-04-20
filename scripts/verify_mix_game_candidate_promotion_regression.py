#!/usr/bin/env python3
"""Run end-to-end regression checks for blocked-family promotion tooling."""

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
    "promotion_candidate_pending_human_review is currently unexercised in the remaining blocked-family set because no other real provenance-complete blocked-family candidate exists in repo scope.",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def family_slug(family_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", family_id.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"root_not_object: {path}")
    return data


def parse_stdout_json(text: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: stdout: line={exc.lineno} col={exc.colno} msg={exc.msg}"


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
    stdout_json, parse_error = parse_stdout_json(completed.stdout)
    return {
        "command": args,
        "exitCode": completed.returncode,
        "stdoutJson": stdout_json,
        "stdoutJsonError": parse_error,
        "stderr": completed.stderr.strip(),
    }


def collect_errors(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    errors = payload.get("errors")
    if isinstance(errors, list):
        return [str(error) for error in errors]
    execution_errors = payload.get("executionErrors")
    if isinstance(execution_errors, list):
        return [str(error) for error in execution_errors]
    return []


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
    candidate_count: int = 0,
    expected_count: int = 0,
    execution_error_count: int = 0,
    failing_candidate_ids: list[str] | None = None,
    deterministic_errors: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "candidateCount": candidate_count,
        "expectedCount": expected_count,
        "executionErrorCount": execution_error_count,
        "failingCandidateIds": failing_candidate_ids or [],
        "deterministicErrors": deterministic_errors or [],
        "details": details or {},
    }


def summarize_validator_failures(
    validator_payload: dict[str, Any],
    *,
    expected_verdict: str,
) -> list[str]:
    failures: list[str] = []
    for result in validator_payload.get("results", []):
        if not isinstance(result, dict):
            failures.append("<invalid-result>")
            continue
        candidate_id = str(result.get("candidateId", "<unknown-candidate>"))
        if result.get("verdict") != expected_verdict:
            failures.append(candidate_id)
        if result.get("executionErrors"):
            failures.append(candidate_id)
    return sorted(set(failures))


def summarize_review_failures(
    review_payload: dict[str, Any],
    *,
    expected_review_verdict: str,
    expected_validator_verdict: str,
) -> list[str]:
    failures: list[str] = []
    for review in review_payload.get("reviews", []):
        if not isinstance(review, dict):
            failures.append("<invalid-review>")
            continue
        candidate_id = str(review.get("candidateId", "<unknown-candidate>"))
        if review.get("reviewVerdict") != expected_review_verdict:
            failures.append(candidate_id)
        if review.get("validatorVerdict") != expected_validator_verdict:
            failures.append(candidate_id)
    return sorted(set(failures))


def run_validate_and_review(
    *,
    repo_root: Path,
    registry_path: Path,
    batch_spec: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    validator_run = run_json_command(
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
    return validator_run, review_run


def scaffold_one(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    family_id: str,
    candidate_id: str,
    notes: str,
) -> dict[str, Any]:
    return run_json_command(
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
            notes,
        ],
        repo_root=repo_root,
    )


def shape_only_one(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    family_id: str,
    candidate_id: str,
    notes: str,
) -> dict[str, Any]:
    return run_json_command(
        [
            sys.executable,
            "scripts/init_mix_game_shape_only_candidates.py",
            "--family",
            family_id,
            "--candidate-id",
            candidate_id,
            "--out-dir",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--expected-verdict",
            SHAPE_ONLY_VALIDATOR_VERDICT,
            "--notes",
            notes,
        ],
        repo_root=repo_root,
    )


def build_staged_batch_spec(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    batch_id: str,
) -> dict[str, Any]:
    return run_json_command(
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


def run_shape_only_controls(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    control_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_promotion_shape_only_"))
    fixture_runs: list[dict[str, Any]] = []
    for family_id in family_ids:
        fixture_runs.append(
            shape_only_one(
                repo_root=repo_root,
                registry_path=registry_path,
                staging_root=control_root,
                family_id=family_id,
                candidate_id=f"shape_only_{family_slug(family_id)}",
                notes="Synthetic shape-only promotion regression control. It is not source evidence.",
            )
        )

    fixture_errors = [
        run
        for run in fixture_runs
        if run["exitCode"] != 0 or not isinstance(run.get("stdoutJson"), dict) or run["stdoutJson"].get("status") != "ok"
    ]

    builder_run: dict[str, Any] | None = None
    validator_run: dict[str, Any] | None = None
    review_run: dict[str, Any] | None = None
    if not fixture_errors:
        builder_run = build_staged_batch_spec(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=control_root,
            batch_id="promotion-regression-synthetic-shape-only-controls",
        )
        if builder_run["exitCode"] == 0 and isinstance(builder_run.get("stdoutJson"), dict):
            validator_run, review_run = run_validate_and_review(
                repo_root=repo_root,
                registry_path=registry_path,
                batch_spec=builder_run["stdoutJson"],
            )

    validator_payload = validator_run.get("stdoutJson") if validator_run else None
    review_payload = review_run.get("stdoutJson") if review_run else None
    validator_summary = validator_payload.get("summary", {}) if isinstance(validator_payload, dict) else {}
    review_summary = review_payload.get("summary", {}) if isinstance(review_payload, dict) else {}

    execution_error_count = len(fixture_errors)
    if builder_run is None:
        execution_error_count += 1
    elif builder_run["exitCode"] != 0 or not isinstance(builder_run.get("stdoutJson"), dict):
        execution_error_count += 1
    if validator_run is None:
        execution_error_count += 1
    elif validator_run["exitCode"] != 0 or not isinstance(validator_payload, dict):
        execution_error_count += 1
    elif isinstance(validator_payload, dict):
        execution_error_count += int(validator_summary.get("executionErrorCount", 0) or 0)
    if review_run is None:
        execution_error_count += 1
    elif review_run["exitCode"] != 0 or not isinstance(review_payload, dict):
        execution_error_count += 1
    elif isinstance(review_payload, dict):
        execution_error_count += int(review_summary.get("reviewExecutionErrorCount", 0) or 0)
        execution_error_count += int(review_summary.get("batchValidatorExecutionErrorCount", 0) or 0)

    failing_ids: list[str] = []
    if isinstance(validator_payload, dict):
        failing_ids.extend(summarize_validator_failures(validator_payload, expected_verdict=SHAPE_ONLY_VALIDATOR_VERDICT))
    if isinstance(review_payload, dict):
        failing_ids.extend(
            summarize_review_failures(
                review_payload,
                expected_review_verdict=SHAPE_ONLY_REVIEW_VERDICT,
                expected_validator_verdict=SHAPE_ONLY_VALIDATOR_VERDICT,
            )
        )
    failing_ids = sorted(set(failing_ids))

    passed = (
        not fixture_errors
        and builder_run is not None
        and builder_run["exitCode"] == 0
        and isinstance(builder_run.get("stdoutJson"), dict)
        and validator_run is not None
        and validator_run["exitCode"] == 0
        and isinstance(validator_payload, dict)
        and validator_payload.get("status") == "ok"
        and validator_summary.get("totalCandidates") == len(family_ids)
        and validator_summary.get("byVerdict", {}).get(SHAPE_ONLY_VALIDATOR_VERDICT) == len(family_ids)
        and validator_summary.get("executionErrorCount") == 0
        and review_run is not None
        and review_run["exitCode"] == 0
        and isinstance(review_payload, dict)
        and review_payload.get("status") == "ok"
        and review_summary.get("totalCandidates") == len(family_ids)
        and review_summary.get("byReviewVerdict", {}).get(SHAPE_ONLY_REVIEW_VERDICT) == len(family_ids)
        and review_summary.get("byValidatorVerdict", {}).get(SHAPE_ONLY_VALIDATOR_VERDICT) == len(family_ids)
        and review_summary.get("falsePositiveRiskCount") == 0
        and review_summary.get("reviewExecutionErrorCount") == 0
        and review_summary.get("batchValidatorExecutionErrorCount") == 0
        and not failing_ids
    )

    return make_subtest_result(
        name="synthetic_shape_only_promotion_controls",
        status="passed" if passed else "failed",
        candidate_count=len(family_ids),
        expected_count=len(family_ids),
        execution_error_count=execution_error_count,
        failing_candidate_ids=failing_ids,
        details={
            "controlRoot": str(control_root),
            "fixtureRunCount": len(fixture_runs),
            "fixtureErrorCount": len(fixture_errors),
            "builderExitCode": None if builder_run is None else builder_run["exitCode"],
            "builderStatus": None if builder_run is None else (builder_run.get("stdoutJson") or {}).get("status"),
            "validatorStatus": None if not isinstance(validator_payload, dict) else validator_payload.get("status"),
            "validatorSummary": validator_summary,
            "reviewStatus": None if not isinstance(review_payload, dict) else review_payload.get("status"),
            "reviewSummary": review_summary,
            "nonGroundingBasis": "Fixtures carry synthetic_shape_only_non_grounding status and placeholder provenance; they are not source evidence.",
        },
    )

def run_template_controls(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    control_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_promotion_templates_"))
    scaffold_runs: list[dict[str, Any]] = []
    for family_id in family_ids:
        scaffold_runs.append(
            scaffold_one(
                repo_root=repo_root,
                registry_path=registry_path,
                staging_root=control_root,
                family_id=family_id,
                candidate_id=f"template_{family_slug(family_id)}",
                notes="Promotion regression scaffold template control only; not source evidence.",
            )
        )

    scaffold_errors = [
        run
        for run in scaffold_runs
        if run["exitCode"] != 0 or not isinstance(run.get("stdoutJson"), dict) or run["stdoutJson"].get("status") != "ok"
    ]

    builder_run: dict[str, Any] | None = None
    validator_run: dict[str, Any] | None = None
    review_run: dict[str, Any] | None = None
    if not scaffold_errors:
        builder_run = build_staged_batch_spec(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=control_root,
            batch_id="promotion-regression-scaffolded-template-controls",
        )
        if builder_run["exitCode"] == 0 and isinstance(builder_run.get("stdoutJson"), dict):
            validator_run, review_run = run_validate_and_review(
                repo_root=repo_root,
                registry_path=registry_path,
                batch_spec=builder_run["stdoutJson"],
            )

    validator_payload = validator_run.get("stdoutJson") if validator_run else None
    review_payload = review_run.get("stdoutJson") if review_run else None
    validator_summary = validator_payload.get("summary", {}) if isinstance(validator_payload, dict) else {}
    review_summary = review_payload.get("summary", {}) if isinstance(review_payload, dict) else {}

    execution_error_count = len(scaffold_errors)
    if builder_run is None:
        execution_error_count += 1
    elif builder_run["exitCode"] != 0 or not isinstance(builder_run.get("stdoutJson"), dict):
        execution_error_count += 1
    if validator_run is None:
        execution_error_count += 1
    elif validator_run["exitCode"] != 0 or not isinstance(validator_payload, dict):
        execution_error_count += 1
    elif isinstance(validator_payload, dict):
        execution_error_count += int(validator_summary.get("executionErrorCount", 0) or 0)
    if review_run is None:
        execution_error_count += 1
    elif review_run["exitCode"] != 0 or not isinstance(review_payload, dict):
        execution_error_count += 1
    elif isinstance(review_payload, dict):
        execution_error_count += int(review_summary.get("reviewExecutionErrorCount", 0) or 0)
        execution_error_count += int(review_summary.get("batchValidatorExecutionErrorCount", 0) or 0)

    failing_ids: list[str] = []
    if isinstance(validator_payload, dict):
        failing_ids.extend(summarize_validator_failures(validator_payload, expected_verdict=TEMPLATE_VALIDATOR_VERDICT))
    if isinstance(review_payload, dict):
        failing_ids.extend(
            summarize_review_failures(
                review_payload,
                expected_review_verdict=TEMPLATE_REVIEW_VERDICT,
                expected_validator_verdict=TEMPLATE_VALIDATOR_VERDICT,
            )
        )
    failing_ids = sorted(set(failing_ids))

    passed = (
        not scaffold_errors
        and builder_run is not None
        and builder_run["exitCode"] == 0
        and isinstance(builder_run.get("stdoutJson"), dict)
        and validator_run is not None
        and validator_run["exitCode"] == 0
        and isinstance(validator_payload, dict)
        and validator_payload.get("status") == "ok"
        and validator_summary.get("totalCandidates") == len(family_ids)
        and validator_summary.get("byVerdict", {}).get(TEMPLATE_VALIDATOR_VERDICT) == len(family_ids)
        and validator_summary.get("executionErrorCount") == 0
        and review_run is not None
        and review_run["exitCode"] == 0
        and isinstance(review_payload, dict)
        and review_payload.get("status") == "ok"
        and review_summary.get("totalCandidates") == len(family_ids)
        and review_summary.get("byReviewVerdict", {}).get(TEMPLATE_REVIEW_VERDICT) == len(family_ids)
        and review_summary.get("byValidatorVerdict", {}).get(TEMPLATE_VALIDATOR_VERDICT) == len(family_ids)
        and review_summary.get("reviewExecutionErrorCount") == 0
        and review_summary.get("batchValidatorExecutionErrorCount") == 0
        and not failing_ids
    )

    return make_subtest_result(
        name="end_to_end_scaffolded_template_controls",
        status="passed" if passed else "failed",
        candidate_count=len(family_ids),
        expected_count=len(family_ids),
        execution_error_count=execution_error_count,
        failing_candidate_ids=failing_ids,
        details={
            "controlRoot": str(control_root),
            "scaffoldRunCount": len(scaffold_runs),
            "scaffoldErrorCount": len(scaffold_errors),
            "builderExitCode": None if builder_run is None else builder_run["exitCode"],
            "builderStatus": None if builder_run is None else (builder_run.get("stdoutJson") or {}).get("status"),
            "validatorStatus": None if not isinstance(validator_payload, dict) else validator_payload.get("status"),
            "validatorSummary": validator_summary,
            "reviewStatus": None if not isinstance(review_payload, dict) else review_payload.get("status"),
            "reviewSummary": review_summary,
        },
    )


def build_grounded_negative_spec(registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for source in GROUNDED_NEGATIVE_SOURCES:
        for family_id in family_ids:
            candidates.append(
                {
                    "candidateId": f"{source['sourceId']}__as__{family_slug(family_id)}",
                    "familyId": family_id,
                    "packPath": source["packPath"],
                    "manifestPath": source["manifestPath"],
                    "expectedVerdict": GROUNDED_VALIDATOR_VERDICT,
                    "notes": "Grounded cc_high / 2-card negative control; must not become a blocked-family promotion candidate.",
                }
            )
    return {
        "batchSpecVersion": "1.0",
        "batchId": "promotion-regression-grounded-negative-controls",
        "description": "Validate grounded cc_high / 2-card artifacts against blocked-family contracts and promotion review as rejection controls.",
        "registryPath": str(registry_path),
        "pathBase": "repo_root",
        "candidates": candidates,
    }


def run_grounded_negative_controls(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    expected_count = len(GROUNDED_NEGATIVE_SOURCES) * len(family_ids)
    validator_run, review_run = run_validate_and_review(
        repo_root=repo_root,
        registry_path=registry_path,
        batch_spec=build_grounded_negative_spec(registry_path, family_ids),
    )
    validator_payload = validator_run.get("stdoutJson")
    review_payload = review_run.get("stdoutJson")
    validator_summary = validator_payload.get("summary", {}) if isinstance(validator_payload, dict) else {}
    review_summary = review_payload.get("summary", {}) if isinstance(review_payload, dict) else {}

    execution_error_count = 0
    if validator_run["exitCode"] != 0 or not isinstance(validator_payload, dict):
        execution_error_count += 1
    elif isinstance(validator_payload, dict):
        execution_error_count += int(validator_summary.get("executionErrorCount", 0) or 0)
    if review_run["exitCode"] != 0 or not isinstance(review_payload, dict):
        execution_error_count += 1
    elif isinstance(review_payload, dict):
        execution_error_count += int(review_summary.get("reviewExecutionErrorCount", 0) or 0)
        execution_error_count += int(review_summary.get("batchValidatorExecutionErrorCount", 0) or 0)

    failing_ids: list[str] = []
    if isinstance(validator_payload, dict):
        failing_ids.extend(summarize_validator_failures(validator_payload, expected_verdict=GROUNDED_VALIDATOR_VERDICT))
    if isinstance(review_payload, dict):
        failing_ids.extend(
            summarize_review_failures(
                review_payload,
                expected_review_verdict=GROUNDED_REVIEW_VERDICT,
                expected_validator_verdict=GROUNDED_VALIDATOR_VERDICT,
            )
        )
    failing_ids = sorted(set(failing_ids))

    passed = (
        validator_run["exitCode"] == 0
        and isinstance(validator_payload, dict)
        and validator_payload.get("status") == "ok"
        and validator_summary.get("totalCandidates") == expected_count
        and validator_summary.get("byVerdict", {}).get(GROUNDED_VALIDATOR_VERDICT) == expected_count
        and validator_summary.get("executionErrorCount") == 0
        and review_run["exitCode"] == 0
        and isinstance(review_payload, dict)
        and review_payload.get("status") == "ok"
        and review_summary.get("totalCandidates") == expected_count
        and review_summary.get("byReviewVerdict", {}).get(GROUNDED_REVIEW_VERDICT) == expected_count
        and review_summary.get("byValidatorVerdict", {}).get(GROUNDED_VALIDATOR_VERDICT) == expected_count
        and review_summary.get("falsePositiveRiskCount") == 0
        and review_summary.get("reviewExecutionErrorCount") == 0
        and review_summary.get("batchValidatorExecutionErrorCount") == 0
        and not failing_ids
    )

    return make_subtest_result(
        name="grounded_negative_promotion_controls",
        status="passed" if passed else "failed",
        candidate_count=expected_count,
        expected_count=expected_count,
        execution_error_count=execution_error_count,
        failing_candidate_ids=failing_ids,
        details={
            "negativeSourceIds": [source["sourceId"] for source in GROUNDED_NEGATIVE_SOURCES],
            "validatorStatus": None if not isinstance(validator_payload, dict) else validator_payload.get("status"),
            "validatorSummary": validator_summary,
            "reviewStatus": None if not isinstance(review_payload, dict) else review_payload.get("status"),
            "reviewSummary": review_summary,
        },
    )


def run_builder_fail_closed_case(
    *,
    repo_root: Path,
    registry_path: Path,
    name: str,
    staging_root: Path,
    expected_error_substring: str,
) -> dict[str, Any]:
    builder_run = build_staged_batch_spec(
        repo_root=repo_root,
        registry_path=registry_path,
        staging_root=staging_root,
        batch_id=f"{name}-promotion-regression",
    )
    payload = builder_run.get("stdoutJson")
    errors = collect_errors(payload)
    matched = any(expected_error_substring in error for error in errors)
    passed = (
        builder_run["exitCode"] != 0
        and isinstance(payload, dict)
        and payload.get("status") == "error"
        and matched
    )
    return make_subtest_result(
        name=name,
        status="passed" if passed else "failed",
        candidate_count=1,
        expected_count=1,
        execution_error_count=len(errors),
        failing_candidate_ids=[] if passed else [name],
        deterministic_errors=errors,
        details={
            "tool": "build_mix_game_candidate_batch_spec.py",
            "stagingRoot": str(staging_root),
            "observedExitCode": builder_run["exitCode"],
            "observedStatus": payload.get("status") if isinstance(payload, dict) else None,
            "expectedErrorSubstring": expected_error_substring,
        },
    )


def run_missing_pack_case(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_promotion_missing_pack_"))
    candidate_id = "malformed_missing_pack"
    scaffold = scaffold_one(
        repo_root=repo_root,
        registry_path=registry_path,
        staging_root=staging_root,
        family_id=family_ids[0],
        candidate_id=candidate_id,
        notes="Malformed promotion regression setup; not source evidence.",
    )
    if scaffold["exitCode"] == 0 and isinstance(scaffold.get("stdoutJson"), dict):
        pack_path = Path(scaffold["stdoutJson"]["candidateDir"]) / "pack.json"
        if pack_path.exists():
            pack_path.unlink()
    return run_builder_fail_closed_case(
        repo_root=repo_root,
        registry_path=registry_path,
        name="malformed_missing_pack_json",
        staging_root=staging_root,
        expected_error_substring=f"missing pack file for {candidate_id}",
    )


def run_duplicate_candidate_case(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_promotion_duplicate_id_"))
    duplicate_id = "duplicate_template_candidate"
    for family_id in family_ids[:2]:
        scaffold_one(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=staging_root,
            family_id=family_id,
            candidate_id=duplicate_id,
            notes="Malformed promotion regression setup; not source evidence.",
        )
    return run_builder_fail_closed_case(
        repo_root=repo_root,
        registry_path=registry_path,
        name="malformed_duplicate_candidate_id",
        staging_root=staging_root,
        expected_error_substring=f"duplicate candidateId in staging build: {duplicate_id}",
    )


def run_unknown_family_case(repo_root: Path, registry_path: Path) -> dict[str, Any]:
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_promotion_unknown_family_"))
    unknown_family = "unknown_blocked_family"
    scaffold_run = run_json_command(
        [
            sys.executable,
            "scripts/init_mix_game_candidate_staging.py",
            "--family",
            unknown_family,
            "--candidate-id",
            "unknown_family_candidate",
            "--out-dir",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--expected-verdict",
            TEMPLATE_VALIDATOR_VERDICT,
        ],
        repo_root=repo_root,
    )
    payload = scaffold_run.get("stdoutJson")
    errors = collect_errors(payload)
    expected = f"unknown family id: {unknown_family}"
    passed = (
        scaffold_run["exitCode"] != 0
        and isinstance(payload, dict)
        and payload.get("status") == "error"
        and any(expected in error for error in errors)
    )
    return make_subtest_result(
        name="malformed_unknown_family_id",
        status="passed" if passed else "failed",
        candidate_count=1,
        expected_count=1,
        execution_error_count=len(errors),
        failing_candidate_ids=[] if passed else ["unknown_family_candidate"],
        deterministic_errors=errors,
        details={
            "tool": "init_mix_game_candidate_staging.py",
            "stagingRoot": str(staging_root),
            "observedExitCode": scaffold_run["exitCode"],
            "observedStatus": payload.get("status") if isinstance(payload, dict) else None,
            "expectedErrorSubstring": expected,
        },
    )


def build_payload(repo_root: Path, registry_path: Path) -> dict[str, Any]:
    registry = load_json_object(registry_path)
    family_ids = get_family_ids(registry)
    if not family_ids:
        return {
            "promotionRegressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "passed",
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "familyIds": [],
            "toolsReused": [
                "scripts/init_mix_game_shape_only_candidates.py",
                "scripts/init_mix_game_candidate_staging.py",
                "scripts/build_mix_game_candidate_batch_spec.py",
                "scripts/validate_mix_game_candidate_batch.py",
                "scripts/validate_mix_game_candidate_family.py",
                "scripts/review_mix_game_candidate_promotion.py",
            ],
            "existingScriptsExtended": True,
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so blocked-family promotion regression is not exercised in this pass."
            ],
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "unexpectedExecutionErrorCount": 0,
                "expectedFailClosedErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "failingSubtests": [],
                "failingCandidateIds": [],
            },
            "subtests": [],
        }
    subtests = [
        run_template_controls(repo_root, registry_path, family_ids),
        run_shape_only_controls(repo_root, registry_path, family_ids),
        run_grounded_negative_controls(repo_root, registry_path, family_ids),
        run_missing_pack_case(repo_root, registry_path, family_ids),
        run_duplicate_candidate_case(repo_root, registry_path, family_ids),
        run_unknown_family_case(repo_root, registry_path),
    ]
    passed = [subtest for subtest in subtests if subtest["status"] == "passed"]
    failed = [subtest for subtest in subtests if subtest["status"] != "passed"]
    expected_fail_closed_errors = sum(
        subtest["executionErrorCount"]
        for subtest in subtests
        if subtest["name"].startswith("malformed_") and subtest["status"] == "passed"
    )
    unexpected_errors = sum(
        subtest["executionErrorCount"]
        for subtest in subtests
        if subtest["status"] != "passed"
    )
    false_positive_count = sum(
        int(subtest.get("details", {}).get("reviewSummary", {}).get("falsePositiveRiskCount", 0) or 0)
        for subtest in subtests
        if subtest["status"] == "passed"
    )

    return {
        "promotionRegressionVersion": REGRESSION_VERSION,
        "repoRoot": str(repo_root),
        "registryPath": str(registry_path),
        "status": "passed" if not failed else "failed",
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "familyIds": family_ids,
        "toolsReused": [
            "scripts/init_mix_game_shape_only_candidates.py",
            "scripts/init_mix_game_candidate_staging.py",
            "scripts/build_mix_game_candidate_batch_spec.py",
            "scripts/validate_mix_game_candidate_batch.py",
            "scripts/validate_mix_game_candidate_family.py",
            "scripts/review_mix_game_candidate_promotion.py",
        ],
        "existingScriptsExtended": True,
        "coverageLimits": COVERAGE_LIMITS,
        "summary": {
            "subtestsTotal": len(subtests),
            "subtestsPassed": len(passed),
            "subtestsFailed": len(failed),
            "unexpectedExecutionErrorCount": unexpected_errors,
            "expectedFailClosedErrorCount": expected_fail_closed_errors,
            "falsePositiveRiskCount": false_positive_count,
            "failingSubtests": [subtest["name"] for subtest in failed],
            "failingCandidateIds": sorted(
                {
                    candidate_id
                    for subtest in failed
                    for candidate_id in subtest.get("failingCandidateIds", [])
                }
            ),
        },
        "subtests": subtests,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default="out/_codex/mix_game_family_contract_registry.json",
        help="Contract registry path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path

    try:
        payload = build_payload(repo_root, registry_path)
    except Exception as exc:  # noqa: BLE001 - top-level regression must fail closed.
        payload = {
            "promotionRegressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "failed",
            "coverageLimits": COVERAGE_LIMITS,
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 1,
                "unexpectedExecutionErrorCount": 1,
                "expectedFailClosedErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "failingSubtests": ["regression_setup"],
                "failingCandidateIds": [],
            },
            "subtests": [
                make_subtest_result(
                    name="regression_setup",
                    status="failed",
                    execution_error_count=1,
                    deterministic_errors=[str(exc)],
                )
            ],
        }

    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
