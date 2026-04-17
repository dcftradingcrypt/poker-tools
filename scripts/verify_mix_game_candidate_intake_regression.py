#!/usr/bin/env python3
"""Run repeatable regression checks for blocked-family intake tooling."""

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
TEMPLATE_VERDICT = "candidate_non_grounding_template_match"
GROUNDED_REJECT_VERDICT = "rejected_wrong_family_markers"
REJECTING_VERDICT_PREFIX = "rejected_"

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


def make_subtest_result(
    *,
    name: str,
    status: str,
    candidate_count: int = 0,
    expected_count: int = 0,
    execution_error_count: int = 0,
    failing_candidate_ids: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "candidateCount": candidate_count,
        "expectedCount": expected_count,
        "executionErrorCount": execution_error_count,
        "failingCandidateIds": failing_candidate_ids or [],
        "details": details or {},
    }


def get_family_ids(registry: dict[str, Any]) -> list[str]:
    boundary = registry.get("currentGroundingBoundary", {})
    blocked = boundary.get("blockedFamilies") if isinstance(boundary, dict) else None
    if isinstance(blocked, list) and all(isinstance(family_id, str) and family_id for family_id in blocked):
        return [str(family_id) for family_id in blocked]

    families = registry.get("families")
    if not isinstance(families, list):
        raise ValueError("registry.families missing_or_not_list")
    ids = [
        entry.get("familyId")
        for entry in families
        if isinstance(entry, dict) and entry.get("currentRepoStatus") == "blocked_no_source"
    ]
    if not all(isinstance(family_id, str) and family_id for family_id in ids):
        raise ValueError("registry.families contains missing blocked familyId")
    return [str(family_id) for family_id in ids]


def summarize_batch_failures(
    batch_payload: dict[str, Any],
    *,
    expected_verdict: str | None = None,
    require_rejecting: bool = False,
) -> list[str]:
    failures: list[str] = []
    for result in batch_payload.get("results", []):
        if not isinstance(result, dict):
            failures.append("<invalid-result>")
            continue
        candidate_id = str(result.get("candidateId", "<unknown-candidate>"))
        verdict = result.get("verdict")
        if expected_verdict is not None and verdict != expected_verdict:
            failures.append(candidate_id)
        elif require_rejecting and not (isinstance(verdict, str) and verdict.startswith(REJECTING_VERDICT_PREFIX)):
            failures.append(candidate_id)
        if result.get("executionErrors"):
            failures.append(candidate_id)
    return sorted(set(failures))


def run_template_controls(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    control_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_intake_templates_"))
    scaffold_runs: list[dict[str, Any]] = []
    for family_id in family_ids:
        candidate_id = f"template_{family_slug(family_id)}"
        scaffold_runs.append(
            run_json_command(
                [
                    sys.executable,
                    "scripts/init_mix_game_candidate_staging.py",
                    "--family",
                    family_id,
                    "--candidate-id",
                    candidate_id,
                    "--out-dir",
                    str(control_root),
                    "--registry",
                    str(registry_path),
                    "--expected-verdict",
                    TEMPLATE_VERDICT,
                    "--notes",
                    "Regression scaffold template control only; not source evidence.",
                ],
                repo_root=repo_root,
            )
        )

    scaffold_errors = [
        run
        for run in scaffold_runs
        if run["exitCode"] != 0 or not isinstance(run.get("stdoutJson"), dict) or run["stdoutJson"].get("status") != "ok"
    ]

    builder_run: dict[str, Any] | None = None
    validator_run: dict[str, Any] | None = None
    if not scaffold_errors:
        builder_run = run_json_command(
            [
                sys.executable,
                "scripts/build_mix_game_candidate_batch_spec.py",
                "--staging-root",
                str(control_root),
                "--registry",
                str(registry_path),
                "--batch-id",
                "scaffolded-template-controls-regression",
            ],
            repo_root=repo_root,
        )
        if builder_run["exitCode"] == 0 and isinstance(builder_run.get("stdoutJson"), dict):
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
                input_payload=builder_run["stdoutJson"],
            )

    validator_payload = validator_run.get("stdoutJson") if validator_run else None
    validator_summary = validator_payload.get("summary", {}) if isinstance(validator_payload, dict) else {}
    failing_ids: list[str] = []
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
        failing_ids = summarize_batch_failures(validator_payload, expected_verdict=TEMPLATE_VERDICT)

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
        and validator_summary.get("byVerdict", {}).get(TEMPLATE_VERDICT) == len(family_ids)
        and validator_summary.get("expectedVerdictMatches") == len(family_ids)
        and validator_summary.get("expectedVerdictMismatches") == 0
        and validator_summary.get("executionErrorCount") == 0
        and not failing_ids
    )

    return make_subtest_result(
        name="scaffolded_template_controls",
        status="passed" if passed else "failed",
        candidate_count=len(family_ids),
        expected_count=len(family_ids),
        execution_error_count=execution_error_count,
        failing_candidate_ids=failing_ids,
        details={
            "controlRoot": str(control_root),
            "scaffoldRunCount": len(scaffold_runs),
            "scaffoldErrorCount": len(scaffold_errors),
            "builderStatus": None if builder_run is None else (builder_run.get("stdoutJson") or {}).get("status"),
            "builderExitCode": None if builder_run is None else builder_run["exitCode"],
            "validatorStatus": None if not isinstance(validator_payload, dict) else validator_payload.get("status"),
            "validatorSummary": validator_summary,
        },
    )


def build_grounded_negative_spec(registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for source in GROUNDED_NEGATIVE_SOURCES:
        for family_id in family_ids:
            family_token = family_slug(family_id)
            candidates.append(
                {
                    "candidateId": f"{source['sourceId']}__as__{family_token}",
                    "familyId": family_id,
                    "packPath": source["packPath"],
                    "manifestPath": source["manifestPath"],
                    "expectedVerdict": GROUNDED_REJECT_VERDICT,
                    "notes": "Grounded cc_high / 2-card negative control; must not match a blocked-family contract.",
                }
            )
    return {
        "batchSpecVersion": "1.0",
        "batchId": "grounded-negative-controls-regression",
        "description": "Validate grounded cc_high / 2-card artifacts against blocked-family contracts as rejection controls.",
        "registryPath": str(registry_path),
        "pathBase": "repo_root",
        "candidates": candidates,
    }


def run_grounded_negative_controls(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    batch_spec = build_grounded_negative_spec(registry_path, family_ids)
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
    payload = validator_run.get("stdoutJson")
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    failing_ids: list[str] = []
    execution_error_count = 0
    if validator_run["exitCode"] != 0 or not isinstance(payload, dict):
        execution_error_count += 1
    elif isinstance(payload, dict):
        execution_error_count += int(summary.get("executionErrorCount", 0) or 0)
        failing_ids = summarize_batch_failures(payload, expected_verdict=GROUNDED_REJECT_VERDICT, require_rejecting=True)

    expected_count = len(GROUNDED_NEGATIVE_SOURCES) * len(family_ids)
    passed = (
        validator_run["exitCode"] == 0
        and isinstance(payload, dict)
        and payload.get("status") == "ok"
        and summary.get("totalCandidates") == expected_count
        and summary.get("byVerdict", {}).get(GROUNDED_REJECT_VERDICT) == expected_count
        and summary.get("expectedVerdictMatches") == expected_count
        and summary.get("expectedVerdictMismatches") == 0
        and summary.get("executionErrorCount") == 0
        and not failing_ids
    )

    return make_subtest_result(
        name="grounded_negative_controls",
        status="passed" if passed else "failed",
        candidate_count=expected_count,
        expected_count=expected_count,
        execution_error_count=execution_error_count,
        failing_candidate_ids=failing_ids,
        details={
            "negativeSourceIds": [source["sourceId"] for source in GROUNDED_NEGATIVE_SOURCES],
            "validatorStatus": None if not isinstance(payload, dict) else payload.get("status"),
            "validatorSummary": summary,
        },
    )


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


def run_builder_fail_closed_case(
    *,
    repo_root: Path,
    registry_path: Path,
    name: str,
    staging_root: Path,
    expected_error_substring: str,
) -> dict[str, Any]:
    builder_run = run_json_command(
        [
            sys.executable,
            "scripts/build_mix_game_candidate_batch_spec.py",
            "--staging-root",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--batch-id",
            f"{name}-regression",
        ],
        repo_root=repo_root,
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
        details={
            "tool": "build_mix_game_candidate_batch_spec.py",
            "stagingRoot": str(staging_root),
            "observedExitCode": builder_run["exitCode"],
            "observedStatus": payload.get("status") if isinstance(payload, dict) else None,
            "expectedErrorSubstring": expected_error_substring,
            "errors": errors,
        },
    )


def scaffold_one(
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    family_id: str,
    candidate_id: str,
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
            TEMPLATE_VERDICT,
            "--notes",
            "Malformed regression setup; not source evidence.",
        ],
        repo_root=repo_root,
    )


def run_missing_pack_case(repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_intake_missing_pack_"))
    candidate_id = "malformed_missing_pack"
    scaffold = scaffold_one(repo_root, registry_path, staging_root, family_ids[0], candidate_id)
    if scaffold["exitCode"] == 0 and isinstance(scaffold.get("stdoutJson"), dict):
        candidate_dir = Path(scaffold["stdoutJson"]["candidateDir"])
        pack_path = candidate_dir / "pack.json"
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
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_intake_duplicate_id_"))
    duplicate_id = "duplicate_template_candidate"
    for family_id in family_ids[:2]:
        scaffold_one(repo_root, registry_path, staging_root, family_id, duplicate_id)
    return run_builder_fail_closed_case(
        repo_root=repo_root,
        registry_path=registry_path,
        name="malformed_duplicate_candidate_id",
        staging_root=staging_root,
        expected_error_substring=f"duplicate candidateId in staging build: {duplicate_id}",
    )


def run_unknown_family_case(repo_root: Path, registry_path: Path) -> dict[str, Any]:
    staging_root = Path(tempfile.mkdtemp(prefix="popker_mix_game_intake_unknown_family_"))
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
            TEMPLATE_VERDICT,
        ],
        repo_root=repo_root,
    )
    payload = scaffold_run.get("stdoutJson")
    errors = collect_errors(payload)
    passed = (
        scaffold_run["exitCode"] != 0
        and isinstance(payload, dict)
        and payload.get("status") == "error"
        and any(f"unknown family id: {unknown_family}" in error for error in errors)
    )
    return make_subtest_result(
        name="malformed_unknown_family_id",
        status="passed" if passed else "failed",
        candidate_count=1,
        expected_count=1,
        execution_error_count=len(errors),
        failing_candidate_ids=[] if passed else ["unknown_family_candidate"],
        details={
            "tool": "init_mix_game_candidate_staging.py",
            "stagingRoot": str(staging_root),
            "observedExitCode": scaffold_run["exitCode"],
            "observedStatus": payload.get("status") if isinstance(payload, dict) else None,
            "expectedErrorSubstring": f"unknown family id: {unknown_family}",
            "errors": errors,
        },
    )


def build_payload(repo_root: Path, registry_path: Path) -> dict[str, Any]:
    registry = load_json_object(registry_path)
    family_ids = get_family_ids(registry)
    if not family_ids:
        return {
            "regressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "passed",
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "familyIds": [],
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "unexpectedExecutionErrorCount": 0,
                "expectedFailClosedErrorCount": 0,
                "failingSubtests": [],
                "failingCandidateIds": [],
            },
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so blocked-family intake regression is not exercised in this pass."
            ],
            "subtests": [],
        }
    subtests = [
        run_template_controls(repo_root, registry_path, family_ids),
        run_grounded_negative_controls(repo_root, registry_path, family_ids),
        run_missing_pack_case(repo_root, registry_path, family_ids),
        run_duplicate_candidate_case(repo_root, registry_path, family_ids),
        run_unknown_family_case(repo_root, registry_path),
    ]
    passed = [subtest for subtest in subtests if subtest["status"] == "passed"]
    failed = [subtest for subtest in subtests if subtest["status"] != "passed"]
    unexpected_errors = sum(
        subtest["executionErrorCount"]
        for subtest in subtests
        if subtest["status"] != "passed"
    )
    fail_closed_error_count = sum(
        subtest["executionErrorCount"]
        for subtest in subtests
        if subtest["name"].startswith("malformed_") and subtest["status"] == "passed"
    )
    return {
        "regressionVersion": REGRESSION_VERSION,
        "repoRoot": str(repo_root),
        "registryPath": str(registry_path),
        "status": "passed" if not failed else "failed",
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "familyIds": family_ids,
        "summary": {
            "subtestsTotal": len(subtests),
            "subtestsPassed": len(passed),
            "subtestsFailed": len(failed),
            "unexpectedExecutionErrorCount": unexpected_errors,
            "expectedFailClosedErrorCount": fail_closed_error_count,
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
    except Exception as exc:  # noqa: BLE001 - top-level CLI must fail closed.
        payload = {
            "regressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "failed",
            "coverageLimits": [],
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 1,
                "unexpectedExecutionErrorCount": 1,
                "expectedFailClosedErrorCount": 0,
                "failingSubtests": ["regression_setup"],
                "failingCandidateIds": [],
            },
            "subtests": [
                make_subtest_result(
                    name="regression_setup",
                    status="failed",
                    execution_error_count=1,
                    failing_candidate_ids=[],
                    details={"error": str(exc)},
                )
            ],
        }

    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
