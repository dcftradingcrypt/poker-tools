#!/usr/bin/env python3
"""Regression checks for blocked-family retained-source seeding."""

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
REGISTRY_REL = "out/_codex/mix_game_family_contract_registry.json"
SEED_STATUS = "retained_sources_seeded_non_grounding"

COVERAGE_LIMITS = [
    "Retained-source seeding records copied files and hashes only; it does not create normalized family-shaped source evidence.",
    "promotion_candidate_pending_human_review remains unexercised because no real provenance-complete candidate exists in the remaining blocked-family set.",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def family_slug(family_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", family_id.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_stdout_json(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: line={exc.lineno} col={exc.colno} msg={exc.msg}"
    if not isinstance(payload, dict):
        return None, "stdout_json_root_not_object"
    return payload, None


def run_json_command(args: list[str], *, repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=repo_root,
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


def command_errors(run: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if run["exitCode"] != 0:
        errors.append(f"command_exit_code={run['exitCode']}")
    if run.get("stdoutJsonError"):
        errors.append(str(run["stdoutJsonError"]))
    if run.get("stderr"):
        errors.append(str(run["stderr"]))
    payload = run.get("stdoutJson")
    if isinstance(payload, dict):
        for error in payload.get("errors", []):
            errors.append(str(error))
        for error in payload.get("executionErrors", []):
            errors.append(str(error))
    return errors


def load_registry(registry_path: Path) -> dict[str, Any]:
    return load_json_file(registry_path)


def family_ids_from_registry(registry: dict[str, Any]) -> list[str]:
    boundary = registry.get("currentGroundingBoundary", {})
    blocked = boundary.get("blockedFamilies") if isinstance(boundary, dict) else None
    if isinstance(blocked, list) and all(isinstance(family_id, str) and family_id for family_id in blocked):
        return [str(family_id) for family_id in blocked]

    families = registry.get("families", [])
    return [
        entry["familyId"]
        for entry in families
        if isinstance(entry, dict)
        and isinstance(entry.get("familyId"), str)
        and entry.get("currentRepoStatus") == "blocked_no_source"
    ]


def make_source_files(root: Path, candidate_id: str, count: int, *, duplicate_basename: bool = False) -> list[Path]:
    source_files: list[Path] = []
    source_root = root / "synthetic_sources" / candidate_id
    source_root.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        if duplicate_basename:
            parent = source_root / f"copy_{index + 1}"
            parent.mkdir()
            path = parent / "same_basename_source.txt"
        else:
            path = source_root / f"retained_source_{index + 1:02d}.txt"
        path.write_text(
            "\n".join(
                [
                    "Synthetic retained-source regression fixture.",
                    f"candidateId={candidate_id}",
                    f"index={index}",
                    "not_real_source_evidence=true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        source_files.append(path)
    return source_files


def init_template_candidate(
    *,
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
            "candidate_non_grounding_template_match",
            "--notes",
            "Source-seed regression template scaffold; not real evidence.",
        ],
        repo_root=repo_root,
    )


def init_shape_only_candidate(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    family_id: str,
    candidate_id: str,
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
            "shape_match_missing_grounding_evidence",
            "--notes",
            "Source-seed regression synthetic shape-only fixture; not real evidence.",
        ],
        repo_root=repo_root,
    )


def seed_candidate(
    *,
    repo_root: Path,
    registry_path: Path,
    candidate_dir: Path,
    source_files: list[Path],
    note: str,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "scripts/seed_mix_game_candidate_sources.py",
        "--candidate-dir",
        str(candidate_dir),
        "--registry",
        str(registry_path),
        "--source-reference",
        "synthetic-regression-reference-not-real-source",
        "--retrieved-at",
        "synthetic-regression-no-real-retrieval-time",
        "--note",
        note,
    ]
    for source_file in source_files:
        command.extend(["--source-file", str(source_file)])
    return run_json_command(command, repo_root=repo_root)


def run_intake(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    batch_id: str,
) -> dict[str, Any]:
    return run_json_command(
        [
            sys.executable,
            "scripts/run_mix_game_candidate_intake.py",
            "--staging-root",
            str(staging_root),
            "--registry",
            str(registry_path),
            "--batch-id",
            batch_id,
        ],
        repo_root=repo_root,
    )


def seed_summary(seed_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidateId": seed_payload.get("candidateId"),
        "familyId": seed_payload.get("familyId"),
        "status": seed_payload.get("status"),
        "copiedSourceCount": len(seed_payload.get("copiedSources", [])),
        "copiedSources": [
            {
                "index": source.get("index"),
                "retainedPath": source.get("retainedPath"),
                "sizeBytes": source.get("sizeBytes"),
            }
            for source in seed_payload.get("copiedSources", [])
            if isinstance(source, dict)
        ],
        "manifestFieldsTouched": seed_payload.get("manifestFieldsTouched", []),
        "metadataFieldsTouched": seed_payload.get("metadataFieldsTouched", []),
        "nonGroundingStatus": seed_payload.get("nonGroundingStatus", {}),
    }


def validate_seed_summaries(seed_summaries: list[dict[str, Any]], *, expected_count: int) -> list[str]:
    failures: list[str] = []
    required_manifest = {"currentRepoStatus", "nonGroundingReason", "provenance.seededRetainedSources"}
    required_metadata = {
        "candidateStatus",
        "currentRepoStatus",
        "nonGroundingReason",
        "seededSourceSummary",
        "templateStatus",
    }
    if len(seed_summaries) != expected_count:
        failures.append(f"seed_summary_count expected={expected_count} actual={len(seed_summaries)}")
    for summary in seed_summaries:
        candidate_id = summary.get("candidateId")
        if summary.get("status") != "ok":
            failures.append(f"{candidate_id}: seed_status_not_ok")
        if summary.get("copiedSourceCount", 0) < 1:
            failures.append(f"{candidate_id}: copiedSourceCount_less_than_1")
        manifest_fields = set(summary.get("manifestFieldsTouched", []))
        metadata_fields = set(summary.get("metadataFieldsTouched", []))
        missing_manifest = sorted(required_manifest - manifest_fields)
        missing_metadata = sorted(required_metadata - metadata_fields)
        if missing_manifest:
            failures.append(f"{candidate_id}: missing_manifest_fields={missing_manifest}")
        if missing_metadata:
            failures.append(f"{candidate_id}: missing_metadata_fields={missing_metadata}")
        non_grounding = summary.get("nonGroundingStatus", {})
        if non_grounding.get("currentRepoStatus") != "blocked_no_source":
            failures.append(f"{candidate_id}: currentRepoStatus_not_blocked_no_source")
        if non_grounding.get("candidateStatus") != SEED_STATUS:
            failures.append(f"{candidate_id}: candidateStatus_not_seeded_non_grounding")
    return failures


def validate_intake_summary(
    *,
    intake_payload: dict[str, Any],
    expected_count: int,
    expected_validator: str,
    expected_review: str,
) -> tuple[list[str], dict[str, Any]]:
    summary = intake_payload.get("summary", {}) if isinstance(intake_payload, dict) else {}
    candidates = intake_payload.get("candidates", []) if isinstance(intake_payload, dict) else []
    failures: list[str] = []
    if intake_payload.get("status") != "ok":
        failures.append(f"intake_status_not_ok: {intake_payload.get('status')}")
    if summary.get("totalCandidates") != expected_count:
        failures.append(f"totalCandidates expected={expected_count} actual={summary.get('totalCandidates')}")
    if summary.get("byValidatorVerdict", {}).get(expected_validator) != expected_count:
        failures.append(f"validator_count {expected_validator} expected={expected_count}")
    if summary.get("byReviewVerdict", {}).get(expected_review) != expected_count:
        failures.append(f"review_count {expected_review} expected={expected_count}")
    if summary.get("executionErrorCount") != 0:
        failures.append(f"executionErrorCount_not_zero: {summary.get('executionErrorCount')}")
    if summary.get("falsePositiveRiskCount") != 0:
        failures.append(f"falsePositiveRiskCount_not_zero: {summary.get('falsePositiveRiskCount')}")
    if summary.get("promotionCandidatePendingHumanReviewCount") != 0:
        failures.append(
            f"promotionCandidatePendingHumanReviewCount_not_zero: {summary.get('promotionCandidatePendingHumanReviewCount')}"
        )
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("currentRepoStatus") != "blocked_no_source":
            failures.append(f"{candidate.get('candidateId')}: currentRepoStatus_not_blocked_no_source")
    compact = {
        "totalCandidates": summary.get("totalCandidates"),
        "byValidatorVerdict": summary.get("byValidatorVerdict", {}),
        "byReviewVerdict": summary.get("byReviewVerdict", {}),
        "executionErrorCount": summary.get("executionErrorCount"),
        "falsePositiveRiskCount": summary.get("falsePositiveRiskCount"),
        "promotionCandidatePendingHumanReviewCount": summary.get("promotionCandidatePendingHumanReviewCount"),
        "nonPromotableCount": summary.get("nonPromotableCount"),
    }
    return failures, compact


def make_result(name: str, *, failures: list[str], details: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "details": details,
    }


def run_seeded_family_controls(
    *,
    repo_root: Path,
    registry_path: Path,
    family_ids: list[str],
    mode: str,
    expected_validator: str,
    expected_review: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"popker_source_seed_{mode}_") as temp_name:
        temp_root = Path(temp_name)
        staging_root = temp_root / "staging"
        seed_summaries: list[dict[str, Any]] = []
        setup_failures: list[str] = []
        for family_id in family_ids:
            slug = family_slug(family_id)
            candidate_id = f"seed_{mode}_{slug}"
            if mode == "template":
                init_run = init_template_candidate(
                    repo_root=repo_root,
                    registry_path=registry_path,
                    staging_root=staging_root,
                    family_id=family_id,
                    candidate_id=candidate_id,
                )
            else:
                init_run = init_shape_only_candidate(
                    repo_root=repo_root,
                    registry_path=registry_path,
                    staging_root=staging_root,
                    family_id=family_id,
                    candidate_id=candidate_id,
                )
            if init_run["exitCode"] != 0 or not isinstance(init_run.get("stdoutJson"), dict):
                setup_failures.append(f"{candidate_id}: init_failed: {command_errors(init_run)}")
                continue
            candidate_dir = Path(init_run["stdoutJson"]["candidateDir"])
            source_files = make_source_files(temp_root, candidate_id, 1)
            seed_run = seed_candidate(
                repo_root=repo_root,
                registry_path=registry_path,
                candidate_dir=candidate_dir,
                source_files=source_files,
                note=f"Synthetic {mode} source-seed regression; not grounding evidence.",
            )
            if seed_run["exitCode"] != 0 or not isinstance(seed_run.get("stdoutJson"), dict):
                setup_failures.append(f"{candidate_id}: seed_failed: {command_errors(seed_run)}")
                continue
            seed_summaries.append(seed_summary(seed_run["stdoutJson"]))

        intake_run = run_intake(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=staging_root,
            batch_id=f"source-seed-regression-{mode}",
        )
        intake_payload = intake_run.get("stdoutJson") if isinstance(intake_run.get("stdoutJson"), dict) else {}
        intake_failures = command_errors(intake_run)
        intake_summary_failures, compact_summary = validate_intake_summary(
            intake_payload=intake_payload,
            expected_count=len(family_ids),
            expected_validator=expected_validator,
            expected_review=expected_review,
        )
        failures = (
            setup_failures
            + validate_seed_summaries(seed_summaries, expected_count=len(family_ids))
            + intake_failures
            + intake_summary_failures
        )
        return make_result(
            f"{mode}_seed_controls",
            failures=failures,
            details={
                "candidateCount": len(family_ids),
                "seededCandidateCount": len(seed_summaries),
                "copiedSourceCount": sum(item.get("copiedSourceCount", 0) for item in seed_summaries),
                "seedSummaries": seed_summaries,
                "intakeSummary": compact_summary,
            },
        )


def run_multi_source_check(*, repo_root: Path, registry_path: Path, family_ids: list[str]) -> dict[str, Any]:
    family_id = family_ids[0]
    slug = family_slug(family_id)
    candidate_id = f"seed_multi_{slug}"
    with tempfile.TemporaryDirectory(prefix="popker_source_seed_multi_") as temp_name:
        temp_root = Path(temp_name)
        staging_root = temp_root / "staging"
        init_run = init_template_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=staging_root,
            family_id=family_id,
            candidate_id=candidate_id,
        )
        setup_failures = command_errors(init_run)
        seed_payload: dict[str, Any] = {}
        compact_summary: dict[str, Any] = {}
        if not setup_failures and isinstance(init_run.get("stdoutJson"), dict):
            source_files = make_source_files(temp_root, candidate_id, 2)
            seed_run = seed_candidate(
                repo_root=repo_root,
                registry_path=registry_path,
                candidate_dir=Path(init_run["stdoutJson"]["candidateDir"]),
                source_files=source_files,
                note="Synthetic multi-source retained-source seed regression; not grounding evidence.",
            )
            setup_failures.extend(command_errors(seed_run))
            if isinstance(seed_run.get("stdoutJson"), dict):
                seed_payload = seed_run["stdoutJson"]
                intake_run = run_intake(
                    repo_root=repo_root,
                    registry_path=registry_path,
                    staging_root=staging_root,
                    batch_id="source-seed-regression-multi-source",
                )
                setup_failures.extend(command_errors(intake_run))
                intake_payload = intake_run.get("stdoutJson") if isinstance(intake_run.get("stdoutJson"), dict) else {}
                intake_failures, compact_summary = validate_intake_summary(
                    intake_payload=intake_payload,
                    expected_count=1,
                    expected_validator="candidate_non_grounding_template_match",
                    expected_review="non_promotable_template_placeholder",
                )
                setup_failures.extend(intake_failures)

        copied = seed_payload.get("copiedSources", []) if isinstance(seed_payload, dict) else []
        retained_paths = [item.get("retainedPath") for item in copied if isinstance(item, dict)]
        indexes = [item.get("index") for item in copied if isinstance(item, dict)]
        expected_paths = ["source/retained_source_01.txt", "source/retained_source_02.txt"]
        failures = list(setup_failures)
        if len(copied) != 2:
            failures.append(f"copiedSources expected=2 actual={len(copied)}")
        if retained_paths != expected_paths:
            failures.append(f"retainedPaths expected={expected_paths} actual={retained_paths}")
        if indexes != [0, 1]:
            failures.append(f"copiedSourceIndexes expected=[0, 1] actual={indexes}")
        fields_failures = validate_seed_summaries([seed_summary(seed_payload)], expected_count=1) if seed_payload else ["seed_payload_missing"]
        failures.extend(fields_failures)
        return make_result(
            "multi_source_seed_verification",
            failures=failures,
            details={
                "candidateId": candidate_id,
                "familyId": family_id,
                "copiedSourceCount": len(copied),
                "retainedPaths": retained_paths,
                "copiedSourceIndexes": indexes,
                "manifestFieldsTouched": seed_payload.get("manifestFieldsTouched", []),
                "metadataFieldsTouched": seed_payload.get("metadataFieldsTouched", []),
                "intakeSummary": compact_summary,
            },
        )


def fail_closed_result(name: str, run: dict[str, Any], expected_fragment: str) -> dict[str, Any]:
    payload = run.get("stdoutJson") if isinstance(run.get("stdoutJson"), dict) else {}
    errors = [str(error) for error in payload.get("errors", [])] if isinstance(payload, dict) else []
    matched = any(expected_fragment in error for error in errors)
    failures: list[str] = []
    if run["exitCode"] == 0:
        failures.append("expected_nonzero_exit")
    if not isinstance(payload, dict) or payload.get("status") != "error":
        failures.append(f"expected_status_error actual={payload.get('status') if isinstance(payload, dict) else None}")
    if not matched:
        failures.append(f"expected_error_fragment_not_found: {expected_fragment}")
    if run.get("stdoutJsonError"):
        failures.append(str(run["stdoutJsonError"]))
    return make_result(
        name,
        failures=failures,
        details={
            "expectedFailClosed": True,
            "expectedErrorFragment": expected_fragment,
            "matchedExpectedError": matched,
            "exitCode": run["exitCode"],
            "status": payload.get("status") if isinstance(payload, dict) else None,
            "errorCount": len(errors),
            "errorFragments": [expected_fragment] if matched else errors,
        },
    )


def run_fail_closed_checks(*, repo_root: Path, registry_path: Path, family_ids: list[str]) -> list[dict[str, Any]]:
    family_id = family_ids[0]
    slug = family_slug(family_id)
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="popker_source_seed_failclosed_") as temp_name:
        temp_root = Path(temp_name)
        source_files = make_source_files(temp_root, "fail_closed_source", 1)

        missing_source_root = temp_root / "missing_source_staging"
        missing_source_init = init_template_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=missing_source_root,
            family_id=family_id,
            candidate_id="fail_missing_source",
        )
        candidate_dir = Path(missing_source_init["stdoutJson"]["candidateDir"])
        missing_source_run = seed_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            candidate_dir=candidate_dir,
            source_files=[temp_root / "no_such_retained_source.txt"],
            note="Malformed missing-source regression.",
        )
        results.append(fail_closed_result("fail_closed_missing_source_file", missing_source_run, "source_file_not_found_or_not_file"))

        missing_dir_run = seed_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            candidate_dir=temp_root / "not_a_candidate_dir",
            source_files=source_files,
            note="Malformed missing-candidate-dir regression.",
        )
        results.append(fail_closed_result("fail_closed_missing_candidate_dir", missing_dir_run, "candidate_dir_not_found"))

        missing_json_dir = temp_root / "missing_json_staging" / slug / "fail_missing_candidate_json"
        missing_json_dir.mkdir(parents=True)
        missing_json_run = seed_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            candidate_dir=missing_json_dir,
            source_files=source_files,
            note="Malformed missing-candidate-json regression.",
        )
        results.append(fail_closed_result("fail_closed_missing_candidate_json", missing_json_run, "missing candidate.json"))

        duplicate_root = temp_root / "duplicate_staging"
        duplicate_init = init_template_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=duplicate_root,
            family_id=family_id,
            candidate_id="fail_duplicate_destination",
        )
        duplicate_sources = make_source_files(temp_root, "fail_duplicate_destination", 2, duplicate_basename=True)
        duplicate_run = seed_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            candidate_dir=Path(duplicate_init["stdoutJson"]["candidateDir"]),
            source_files=duplicate_sources,
            note="Malformed duplicate-destination regression.",
        )
        results.append(fail_closed_result("fail_closed_duplicate_destination_name", duplicate_run, "duplicate destination source filename"))

        mismatch_root = temp_root / "family_mismatch_staging"
        mismatch_init = init_template_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            staging_root=mismatch_root,
            family_id=family_id,
            candidate_id="fail_family_mismatch",
        )
        mismatch_candidate_dir = Path(mismatch_init["stdoutJson"]["candidateDir"])
        metadata_path = mismatch_candidate_dir / "candidate.json"
        metadata = load_json_file(metadata_path)
        metadata["familyId"] = "unknown_seed_family"
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        mismatch_run = seed_candidate(
            repo_root=repo_root,
            registry_path=registry_path,
            candidate_dir=mismatch_candidate_dir,
            source_files=source_files,
            note="Malformed family-mismatch regression.",
        )
        results.append(fail_closed_result("fail_closed_family_mismatch", mismatch_run, "candidate.json familyId not in registry"))

    return results


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    failing = [result for result in results if result.get("status") != "passed"]
    expected_fail_closed = [result for result in results if result.get("details", {}).get("expectedFailClosed")]
    template = next((result for result in results if result["name"] == "template_seed_controls"), {})
    shape = next((result for result in results if result["name"] == "shape_seed_controls"), {})
    multi = next((result for result in results if result["name"] == "multi_source_seed_verification"), {})

    false_positive_count = 0
    promotion_candidate_count = 0
    for result in results:
        details = result.get("details", {})
        summary = details.get("intakeSummary", {})
        if isinstance(summary, dict):
            false_positive_count += int(summary.get("falsePositiveRiskCount") or 0)
            promotion_candidate_count += int(summary.get("promotionCandidatePendingHumanReviewCount") or 0)

    return {
        "subtestsTotal": len(results),
        "subtestsPassed": len(results) - len(failing),
        "subtestsFailed": len(failing),
        "templateSeedCandidates": template.get("details", {}).get("candidateCount", 0),
        "shapeOnlySeedCandidates": shape.get("details", {}).get("candidateCount", 0),
        "multiSourceCandidates": 1 if multi.get("status") == "passed" else 0,
        "expectedFailClosedErrorCount": len(expected_fail_closed),
        "unexpectedExecutionErrorCount": sum(len(result.get("failures", [])) for result in failing),
        "falsePositiveRiskCount": false_positive_count,
        "promotionCandidatePendingHumanReviewCount": promotion_candidate_count,
        "failingSubtests": [result["name"] for result in failing],
        "failingCandidateIds": sorted(
            {
                item.get("candidateId")
                for result in results
                for item in result.get("details", {}).get("seedSummaries", [])
                if result.get("status") != "passed" and isinstance(item, dict) and item.get("candidateId")
            }
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=REGISTRY_REL,
        help="Blocked-family contract registry path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    registry = load_registry(registry_path)
    family_ids = family_ids_from_registry(registry)
    if not family_ids:
        payload = {
            "sourceSeedRegressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "ok",
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "familyIds": [],
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so blocked-family source-seed regression is not exercised in this pass."
            ],
            "toolsReused": [
                "scripts/seed_mix_game_candidate_sources.py",
                "scripts/init_mix_game_candidate_staging.py",
                "scripts/init_mix_game_shape_only_candidates.py",
                "scripts/run_mix_game_candidate_intake.py",
            ],
            "existingScriptsExtended": [],
            "summary": {
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "expectedFailClosedErrorCount": 0,
                "unexpectedExecutionErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "promotionCandidatePendingHumanReviewCount": 0,
            },
            "subtests": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    results: list[dict[str, Any]] = []
    results.append(
        run_seeded_family_controls(
            repo_root=repo_root,
            registry_path=registry_path,
            family_ids=family_ids,
            mode="template",
            expected_validator="candidate_non_grounding_template_match",
            expected_review="non_promotable_template_placeholder",
        )
    )
    results.append(
        run_seeded_family_controls(
            repo_root=repo_root,
            registry_path=registry_path,
            family_ids=family_ids,
            mode="shape",
            expected_validator="shape_match_missing_grounding_evidence",
            expected_review="family_shape_match_missing_grounding_evidence",
        )
    )
    results.append(run_multi_source_check(repo_root=repo_root, registry_path=registry_path, family_ids=family_ids))
    results.extend(run_fail_closed_checks(repo_root=repo_root, registry_path=registry_path, family_ids=family_ids))

    summary = summarize_results(results)
    payload = {
        "sourceSeedRegressionVersion": REGRESSION_VERSION,
        "repoRoot": str(repo_root),
        "registryPath": str(registry_path),
        "status": "ok" if summary["subtestsFailed"] == 0 else "failed",
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "familyIds": family_ids,
        "coverageLimits": COVERAGE_LIMITS,
        "toolsReused": [
            "scripts/seed_mix_game_candidate_sources.py",
            "scripts/init_mix_game_candidate_staging.py",
            "scripts/init_mix_game_shape_only_candidates.py",
            "scripts/run_mix_game_candidate_intake.py",
        ],
        "existingScriptsExtended": [],
        "summary": summary,
        "subtests": results,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
