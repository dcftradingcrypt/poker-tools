#!/usr/bin/env python3
"""Aggregate blocked-family intake regression lanes into one healthcheck.

This script intentionally does not validate candidate families itself. It runs the
existing lane-specific regression scripts and reports whether their structured
outputs still preserve the current blocked-family grounding boundary.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


TOOLCHAIN_HEALTH_VERSION = "1.0"
DEFAULT_REGISTRY = "out/_codex/mix_game_family_contract_registry.json"
PASSING_COMPONENT_PAYLOAD_STATUSES = {"passed", "ok"}
COMPONENTS = [
    {
        "componentId": "candidate_intake_regression",
        "scriptPath": "scripts/verify_mix_game_candidate_intake_regression.py",
    },
    {
        "componentId": "candidate_promotion_regression",
        "scriptPath": "scripts/verify_mix_game_candidate_promotion_regression.py",
    },
    {
        "componentId": "candidate_intake_entrypoint_regression",
        "scriptPath": "scripts/verify_mix_game_candidate_intake_entrypoint_regression.py",
    },
    {
        "componentId": "candidate_source_seed_regression",
        "scriptPath": "scripts/verify_mix_game_candidate_source_seed_regression.py",
    },
    {
        "componentId": "source_drop_workflow_regression",
        "scriptPath": "scripts/verify_mix_game_source_drop_workflow_regression.py",
    },
]
PROMOTION_REVIEW_COVERAGE_LIMIT = (
    "promotion_candidate_pending_human_review remains unexercised because no real "
    "provenance-complete candidate exists in the remaining blocked-family set."
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_path(path_arg: str, root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return root / path


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def registry_family_ids(registry: dict[str, Any]) -> list[str]:
    boundary = registry.get("currentGroundingBoundary", {})
    blocked = boundary.get("blockedFamilies") if isinstance(boundary, dict) else None
    if isinstance(blocked, list):
        ids = [family_id for family_id in blocked if isinstance(family_id, str)]
        if len(ids) == len(blocked):
            return ids

    families = registry.get("families", [])
    if not isinstance(families, list):
        return []
    ids: list[str] = []
    for family in families:
        if (
            isinstance(family, dict)
            and isinstance(family.get("familyId"), str)
            and family.get("currentRepoStatus") == "blocked_no_source"
        ):
            ids.append(family["familyId"])
    return ids


def registry_boundary(registry: dict[str, Any]) -> dict[str, Any]:
    boundary = registry.get("currentGroundingBoundary")
    return boundary if isinstance(boundary, dict) else {}


def parse_stdout_json(stdout: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json_stdout: {exc.msg}"
    if not isinstance(parsed, dict):
        return None, "invalid_json_stdout: top-level value is not an object"
    return parsed, None


def coerce_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def component_execution_errors(
    payload: dict[str, Any] | None,
    exit_code: int | None,
    parse_error: str | None,
    stderr: str,
) -> list[str]:
    errors: list[str] = []
    if exit_code is None:
        errors.append("component_not_executed")
    elif exit_code != 0:
        errors.append(f"component_exit_code_nonzero:{exit_code}")
    if parse_error:
        errors.append(parse_error)
    if stderr.strip():
        errors.append(f"component_stderr:{stderr.strip()}")
    if isinstance(payload, dict):
        payload_errors = payload.get("executionErrors")
        if isinstance(payload_errors, list):
            for item in payload_errors:
                if isinstance(item, str):
                    errors.append(item)
                elif item:
                    errors.append(json.dumps(item, sort_keys=True))
    return errors


def run_component(component: dict[str, str], root: Path, registry_path: Path) -> dict[str, Any]:
    script_path = root / component["scriptPath"]
    if not script_path.is_file():
        error = f"missing_component_script:{component['scriptPath']}"
        return {
            "componentId": component["componentId"],
            "scriptPath": component["scriptPath"],
            "status": "failed",
            "payloadStatus": None,
            "exitCode": None,
            "summary": {},
            "coverageLimits": [],
            "familyIds": [],
            "currentGroundingBoundary": {},
            "payloadTopLevelKeys": [],
            "executionErrors": [error],
        }

    completed = subprocess.run(
        [sys.executable, component["scriptPath"], "--registry", str(registry_path)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    payload, parse_error = parse_stdout_json(completed.stdout)
    payload_status = payload.get("status") if isinstance(payload, dict) else None
    passing = completed.returncode == 0 and payload_status in PASSING_COMPONENT_PAYLOAD_STATUSES and parse_error is None
    summary = payload.get("summary", {}) if isinstance(payload, dict) and isinstance(payload.get("summary"), dict) else {}
    coverage_limits = (
        payload.get("coverageLimits", [])
        if isinstance(payload, dict) and isinstance(payload.get("coverageLimits"), list)
        else []
    )
    family_ids = payload.get("familyIds", []) if isinstance(payload, dict) and isinstance(payload.get("familyIds"), list) else []
    boundary = (
        payload.get("currentGroundingBoundary", {})
        if isinstance(payload, dict) and isinstance(payload.get("currentGroundingBoundary"), dict)
        else {}
    )
    return {
        "componentId": component["componentId"],
        "scriptPath": component["scriptPath"],
        "status": "passed" if passing else "failed",
        "payloadStatus": payload_status,
        "exitCode": completed.returncode,
        "summary": summary,
        "coverageLimits": coverage_limits,
        "familyIds": family_ids,
        "currentGroundingBoundary": boundary,
        "payloadTopLevelKeys": sorted(payload.keys()) if isinstance(payload, dict) else [],
        "executionErrors": component_execution_errors(payload, completed.returncode, parse_error, completed.stderr),
    }


def expected_boundary(boundary: dict[str, Any]) -> dict[str, list[str]]:
    grounded = boundary.get("groundedFamilies")
    blocked = boundary.get("blockedFamilies")
    return {
        "grounded": grounded if isinstance(grounded, list) else [],
        "blocked": blocked if isinstance(blocked, list) else [],
    }


def observed_boundary(boundary: dict[str, Any]) -> dict[str, list[str]] | None:
    if not boundary:
        return None
    if isinstance(boundary.get("groundedFamilies"), list) or isinstance(boundary.get("blockedFamilies"), list):
        return {
            "grounded": boundary.get("groundedFamilies") if isinstance(boundary.get("groundedFamilies"), list) else [],
            "blocked": boundary.get("blockedFamilies") if isinstance(boundary.get("blockedFamilies"), list) else [],
        }
    if isinstance(boundary.get("grounded"), list) or isinstance(boundary.get("blocked_no_source"), list):
        return {
            "grounded": boundary.get("grounded") if isinstance(boundary.get("grounded"), list) else [],
            "blocked": boundary.get("blocked_no_source") if isinstance(boundary.get("blocked_no_source"), list) else [],
        }
    return None


def boundary_consistency_errors(
    component_runs: list[dict[str, Any]], family_ids: list[str], boundary: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    expected = expected_boundary(boundary)
    expected_families = set(family_ids)
    for run in component_runs:
        component_id = run["componentId"]
        observed_families = run.get("familyIds", [])
        if observed_families and set(observed_families) != expected_families:
            errors.append(f"{component_id}:familyIds_mismatch")
        normalized_boundary = observed_boundary(run.get("currentGroundingBoundary", {}))
        if normalized_boundary is None:
            continue
        if set(normalized_boundary["blocked"]) != set(expected["blocked"]):
            errors.append(f"{component_id}:blocked_boundary_mismatch")
        if set(normalized_boundary["grounded"]) != set(expected["grounded"]):
            errors.append(f"{component_id}:grounded_boundary_mismatch")
    return errors


def unique_strings(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = item if isinstance(item, str) else json.dumps(item, sort_keys=True)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def summarize(component_runs: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [run.get("summary", {}) for run in component_runs if isinstance(run.get("summary"), dict)]
    failing_components = [run["componentId"] for run in component_runs if run.get("status") != "passed"]
    return {
        "componentCount": len(component_runs),
        "passedComponentCount": sum(1 for run in component_runs if run.get("status") == "passed"),
        "failedComponentCount": len(failing_components),
        "componentIds": [run["componentId"] for run in component_runs],
        "subtestsTotal": sum(coerce_int(summary.get("subtestsTotal")) for summary in summaries),
        "subtestsPassed": sum(coerce_int(summary.get("subtestsPassed")) for summary in summaries),
        "subtestsFailed": sum(coerce_int(summary.get("subtestsFailed")) for summary in summaries),
        "expectedFailClosedErrorCount": sum(
            coerce_int(summary.get("expectedFailClosedErrorCount")) for summary in summaries
        ),
        "unexpectedExecutionErrorCount": sum(
            coerce_int(summary.get("unexpectedExecutionErrorCount")) for summary in summaries
        ),
        "falsePositiveRiskCount": sum(coerce_int(summary.get("falsePositiveRiskCount")) for summary in summaries),
        "promotionCandidatePendingHumanReviewCount": sum(
            coerce_int(summary.get("promotionCandidatePendingHumanReviewCount")) for summary in summaries
        ),
        "failingComponents": failing_components,
    }


def build_health_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    registry_path = resolve_path(args.registry, root)
    execution_errors: list[str] = []
    try:
        registry = load_json_object(registry_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        registry = {}
        execution_errors.append(f"registry_load_failed:{exc}")

    family_ids = registry_family_ids(registry)
    boundary = registry_boundary(registry)
    if registry and not family_ids:
        return {
            "toolchainHealthVersion": TOOLCHAIN_HEALTH_VERSION,
            "repoRoot": root.as_posix(),
            "registryPath": display_path(registry_path, root),
            "status": "passed",
            "currentGroundingBoundary": boundary,
            "blockedFamilyIds": [],
            "componentRuns": [],
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so the blocked-family toolchain is not exercised in this pass."
            ],
            "summary": {
                "componentCount": 0,
                "passedComponentCount": 0,
                "failedComponentCount": 0,
                "componentIds": [],
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "expectedFailClosedErrorCount": 0,
                "unexpectedExecutionErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "promotionCandidatePendingHumanReviewCount": 0,
                "failingComponents": [],
                "boundaryConsistent": True,
                "registryFamilyCount": 0,
            },
            "executionErrors": [],
        }
    component_runs = [run_component(component, root, registry_path) for component in COMPONENTS] if registry else []
    execution_errors.extend(boundary_consistency_errors(component_runs, family_ids, boundary))
    summary = summarize(component_runs)
    summary["boundaryConsistent"] = not any(error.endswith("_boundary_mismatch") for error in execution_errors)
    summary["registryFamilyCount"] = len(family_ids)

    component_errors = [
        f"{run['componentId']}:{error}"
        for run in component_runs
        for error in run.get("executionErrors", [])
        if error
    ]
    all_execution_errors = unique_strings(execution_errors + component_errors)
    coverage_limits = unique_strings(
        [PROMOTION_REVIEW_COVERAGE_LIMIT]
        + [
            limit
            for run in component_runs
            for limit in run.get("coverageLimits", [])
            if isinstance(limit, str)
        ]
    )
    status = "passed" if summary["failedComponentCount"] == 0 and not all_execution_errors else "failed"
    return {
        "toolchainHealthVersion": TOOLCHAIN_HEALTH_VERSION,
        "repoRoot": root.as_posix(),
        "registryPath": display_path(registry_path, root),
        "status": status,
        "currentGroundingBoundary": boundary,
        "blockedFamilyIds": family_ids,
        "componentRuns": component_runs,
        "coverageLimits": coverage_limits,
        "summary": summary,
        "executionErrors": all_execution_errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY,
        help="Path to the blocked-family contract registry JSON.",
    )
    return parser.parse_args()


def main() -> int:
    payload = build_health_payload(parse_args())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
