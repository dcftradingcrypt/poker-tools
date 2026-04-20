#!/usr/bin/env python3
"""Regression checks for the blocked-family source-drop workflow entrypoint."""

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

TEMPLATE_VALIDATOR_VERDICT = "candidate_non_grounding_template_match"
TEMPLATE_REVIEW_VERDICT = "non_promotable_template_placeholder"
SHAPE_ONLY_VALIDATOR_VERDICT = "shape_match_missing_grounding_evidence"
SHAPE_ONLY_REVIEW_VERDICT = "family_shape_match_missing_grounding_evidence"

REQUIRED_DOSSIER_KEYS = [
    "sourceDropWorkflowVersion",
    "mode",
    "status",
    "registryPath",
    "currentGroundingBoundary",
    "candidateDir",
    "familyId",
    "candidateId",
    "scaffoldResult_or_null",
    "sourceSeedResult",
    "generatedBatchSpec",
    "intakeDossier",
    "executionErrors",
    "warnings",
    "coverageLimits",
    "summary",
]

COVERAGE_LIMITS = [
    "Retained-source seeding records copied files and hashes only; it does not create normalized family-shaped source evidence.",
    "Synthetic shape-only fixtures exercise family_shape_match_missing_grounding_evidence without creating source evidence.",
    "promotion_candidate_pending_human_review remains unexercised because no real provenance-complete candidate exists in the remaining blocked-family set.",
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


def run_command(args: list[str], *, repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=repo_root,
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
        for key in ("errors", "executionErrors"):
            values = payload.get(key)
            if isinstance(values, list):
                for value in values:
                    errors.append(str(value))
    return errors


def family_ids_from_registry(registry: dict[str, Any]) -> list[str]:
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


def make_source_files(root: Path, candidate_id: str, count: int) -> list[Path]:
    source_dir = root / "synthetic_retained_sources" / candidate_id
    source_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index in range(count):
        path = source_dir / f"retained_source_{index + 1:02d}.txt"
        path.write_text(
            "\n".join(
                [
                    "Synthetic retained source for source-drop workflow regression.",
                    f"candidateId={candidate_id}",
                    f"sourceIndex={index}",
                    "notRealSourceEvidence=true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def run_shape_only_init(
    *,
    repo_root: Path,
    registry_path: Path,
    staging_root: Path,
    family_id: str,
    candidate_id: str,
) -> dict[str, Any]:
    return run_command(
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
            "Source-drop workflow regression synthetic shape-only fixture; not real evidence.",
        ],
        repo_root=repo_root,
    )


def run_workflow(
    *,
    repo_root: Path,
    registry_path: Path,
    source_files: list[Path],
    output_path: Path | None = None,
    candidate_dir: Path | None = None,
    family_id: str | None = None,
    candidate_id: str | None = None,
    staging_root: Path | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any], str | None]:
    command = [sys.executable, "scripts/run_mix_game_source_drop_workflow.py", "--registry", str(registry_path)]
    if candidate_dir is not None:
        command.extend(["--candidate-dir", str(candidate_dir)])
    else:
        assert family_id is not None
        assert candidate_id is not None
        assert staging_root is not None
        command.extend(["--family", family_id, "--candidate-id", candidate_id, "--staging-root", str(staging_root)])
    for source_file in source_files:
        command.extend(["--source-file", str(source_file)])
    command.extend(["--source-reference", "synthetic-regression-reference-not-real-source"])
    command.extend(["--retrieved-at", "synthetic-regression-no-real-retrieval-time"])
    command.extend(["--note", "Synthetic source-drop workflow regression input; not grounding evidence."])
    if output_path is not None:
        command.extend(["--output", str(output_path)])

    run = run_command(command, repo_root=repo_root)
    if output_path is not None:
        try:
            payload = load_json_object(output_path)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
            return None, run, f"output_json_read_error: {exc}"
        return payload, run, None
    if isinstance(run.get("stdoutJson"), dict):
        return run["stdoutJson"], run, None
    return None, run, run.get("stdoutJsonError") or "stdout_json_missing"


def dossier_schema_failures(dossier: dict[str, Any] | None) -> list[str]:
    if not isinstance(dossier, dict):
        return ["dossier_missing_or_not_object"]
    return [f"missing_dossier_key={key}" for key in REQUIRED_DOSSIER_KEYS if key not in dossier]


def workflow_compact_summary(dossier: dict[str, Any] | None) -> dict[str, Any]:
    summary = dossier.get("summary", {}) if isinstance(dossier, dict) else {}
    source_seed = dossier.get("sourceSeedResult", {}) if isinstance(dossier, dict) else {}
    copied_sources = source_seed.get("copiedSources", []) if isinstance(source_seed, dict) else []
    return {
        "mode": dossier.get("mode") if isinstance(dossier, dict) else None,
        "status": dossier.get("status") if isinstance(dossier, dict) else None,
        "candidateId": dossier.get("candidateId") if isinstance(dossier, dict) else None,
        "familyId": dossier.get("familyId") if isinstance(dossier, dict) else None,
        "validatorVerdict": summary.get("targetValidatorVerdict"),
        "reviewVerdict": summary.get("targetReviewVerdict"),
        "copiedSourceCount": summary.get("copiedSourceCount"),
        "executionErrorCount": summary.get("executionErrorCount"),
        "intakeExecutionErrorCount": summary.get("intakeExecutionErrorCount"),
        "falsePositiveRiskCount": summary.get("falsePositiveRiskCount"),
        "promotionCandidatePendingHumanReviewCount": summary.get("promotionCandidatePendingHumanReviewCount"),
        "targetStillNonPromotable": summary.get("targetStillNonPromotable"),
        "currentRepoStatusPreserved": summary.get("currentRepoStatusPreserved"),
        "retainedPaths": [
            item.get("retainedPath")
            for item in copied_sources
            if isinstance(item, dict)
        ],
        "copiedSourceIndexes": [
            item.get("index")
            for item in copied_sources
            if isinstance(item, dict)
        ],
        "manifestFieldsTouched": source_seed.get("manifestFieldsTouched", []) if isinstance(source_seed, dict) else [],
        "metadataFieldsTouched": source_seed.get("metadataFieldsTouched", []) if isinstance(source_seed, dict) else [],
    }


def validate_workflow_dossier(
    dossier: dict[str, Any] | None,
    *,
    expected_mode: str,
    expected_validator: str,
    expected_review: str,
    expected_source_count: int,
) -> list[str]:
    failures = dossier_schema_failures(dossier)
    if not isinstance(dossier, dict):
        return failures
    summary = dossier.get("summary", {})
    if dossier.get("status") != "ok":
        failures.append(f"workflow_status_not_ok: {dossier.get('status')}")
    if dossier.get("mode") != expected_mode:
        failures.append(f"mode expected={expected_mode} actual={dossier.get('mode')}")
    if summary.get("targetValidatorVerdict") != expected_validator:
        failures.append(f"validator expected={expected_validator} actual={summary.get('targetValidatorVerdict')}")
    if summary.get("targetReviewVerdict") != expected_review:
        failures.append(f"review expected={expected_review} actual={summary.get('targetReviewVerdict')}")
    if summary.get("copiedSourceCount") != expected_source_count:
        failures.append(f"copiedSourceCount expected={expected_source_count} actual={summary.get('copiedSourceCount')}")
    if summary.get("executionErrorCount") != 0:
        failures.append(f"executionErrorCount_not_zero: {summary.get('executionErrorCount')}")
    if summary.get("intakeExecutionErrorCount") != 0:
        failures.append(f"intakeExecutionErrorCount_not_zero: {summary.get('intakeExecutionErrorCount')}")
    if summary.get("falsePositiveRiskCount") != 0:
        failures.append(f"falsePositiveRiskCount_not_zero: {summary.get('falsePositiveRiskCount')}")
    if summary.get("promotionCandidatePendingHumanReviewCount") != 0:
        failures.append(
            f"promotionCandidatePendingHumanReviewCount_not_zero: {summary.get('promotionCandidatePendingHumanReviewCount')}"
        )
    if summary.get("targetStillNonPromotable") is not True:
        failures.append("targetStillNonPromotable_not_true")
    if summary.get("currentRepoStatusPreserved") is not True:
        failures.append("currentRepoStatusPreserved_not_true")
    if dossier.get("familyId") not in dossier.get("currentGroundingBoundary", {}).get("blockedFamilies", []):
        failures.append(f"familyId_not_in_blocked_boundary: {dossier.get('familyId')}")
    return failures


def make_subtest(
    name: str,
    *,
    failures: list[str],
    details: dict[str, Any],
    candidate_count: int = 0,
    expected_count: int = 0,
    expected_fail_closed: bool = False,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": "passed" if not failures else "failed",
        "candidateCount": candidate_count,
        "expectedCount": expected_count,
        "executionErrorCount": 0 if not failures else len(failures),
        "expectedFailClosed": expected_fail_closed,
        "failures": failures,
        "details": details,
    }


def summarize_control_dossiers(dossiers: list[dict[str, Any]]) -> dict[str, Any]:
    validator_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    execution_errors = 0
    false_positive = 0
    promotion_pending = 0
    copied_sources = 0
    for dossier in dossiers:
        summary = dossier.get("summary", {})
        validator = summary.get("targetValidatorVerdict")
        review = summary.get("targetReviewVerdict")
        if isinstance(validator, str):
            validator_counts[validator] = validator_counts.get(validator, 0) + 1
        if isinstance(review, str):
            review_counts[review] = review_counts.get(review, 0) + 1
        execution_errors += int(summary.get("executionErrorCount") or 0)
        false_positive += int(summary.get("falsePositiveRiskCount") or 0)
        promotion_pending += int(summary.get("promotionCandidatePendingHumanReviewCount") or 0)
        copied_sources += int(summary.get("copiedSourceCount") or 0)
    return {
        "totalCandidates": len(dossiers),
        "byValidatorVerdict": dict(sorted(validator_counts.items())),
        "byReviewVerdict": dict(sorted(review_counts.items())),
        "copiedSourceCount": copied_sources,
        "executionErrorCount": execution_errors,
        "falsePositiveRiskCount": false_positive,
        "promotionCandidatePendingHumanReviewCount": promotion_pending,
    }


def run_template_mode_controls(
    *,
    repo_root: Path,
    registry_path: Path,
    family_ids: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="popker_source_drop_template_") as temp_name:
        temp_root = Path(temp_name)
        staging_root = temp_root / "staging"
        output_path = temp_root / "workflow_outputs" / "template_mode_output.json"
        dossiers: list[dict[str, Any]] = []
        compact: list[dict[str, Any]] = []
        failures: list[str] = []
        output_verification: dict[str, Any] = {"checked": False}

        for index, family_id in enumerate(family_ids):
            slug = family_slug(family_id)
            candidate_id = f"workflow_template_{slug}"
            source_files = make_source_files(temp_root, candidate_id, 2 if index == 0 else 1)
            out_path = output_path if index == 0 else None
            dossier, run, output_error = run_workflow(
                repo_root=repo_root,
                registry_path=registry_path,
                family_id=family_id,
                candidate_id=candidate_id,
                staging_root=staging_root,
                source_files=source_files,
                output_path=out_path,
            )
            if output_error:
                failures.append(f"{candidate_id}: {output_error}")
            failures.extend(f"{candidate_id}: {failure}" for failure in command_errors(run))
            failures.extend(
                f"{candidate_id}: {failure}"
                for failure in validate_workflow_dossier(
                    dossier,
                    expected_mode="scaffold_new",
                    expected_validator=TEMPLATE_VALIDATOR_VERDICT,
                    expected_review=TEMPLATE_REVIEW_VERDICT,
                    expected_source_count=2 if index == 0 else 1,
                )
            )
            if isinstance(dossier, dict):
                dossiers.append(dossier)
                compact.append(workflow_compact_summary(dossier))
                if index == 0:
                    output_verification = {
                        "checked": True,
                        "mode": "scaffold_new",
                        "path": str(output_path),
                        "schemaMatched": not dossier_schema_failures(dossier),
                        "status": dossier.get("status"),
                    }

        details = {
            "summary": summarize_control_dossiers(dossiers),
            "candidateSummaries": compact,
            "outputFileVerification": output_verification,
        }
        return make_subtest(
            "template_mode_scaffold_new_controls",
            failures=failures,
            details=details,
            candidate_count=len(dossiers),
            expected_count=len(family_ids),
        ), output_verification


def run_shape_only_mode_controls(
    *,
    repo_root: Path,
    registry_path: Path,
    family_ids: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="popker_source_drop_shape_only_") as temp_name:
        temp_root = Path(temp_name)
        staging_root = temp_root / "shape_staging"
        output_path = temp_root / "workflow_outputs" / "shape_only_existing_mode_output.json"
        dossiers: list[dict[str, Any]] = []
        compact: list[dict[str, Any]] = []
        failures: list[str] = []
        output_verification: dict[str, Any] = {"checked": False}

        for index, family_id in enumerate(family_ids):
            slug = family_slug(family_id)
            candidate_id = f"workflow_shape_{slug}"
            init_run = run_shape_only_init(
                repo_root=repo_root,
                registry_path=registry_path,
                staging_root=staging_root,
                family_id=family_id,
                candidate_id=candidate_id,
            )
            failures.extend(f"{candidate_id}: shape_only_init: {failure}" for failure in command_errors(init_run))
            init_payload = init_run.get("stdoutJson") if isinstance(init_run.get("stdoutJson"), dict) else None
            if not isinstance(init_payload, dict) or init_payload.get("status") != "ok":
                failures.append(f"{candidate_id}: shape_only_init_payload_not_ok")
                continue

            source_files = make_source_files(temp_root, candidate_id, 1)
            out_path = output_path if index == 0 else None
            dossier, run, output_error = run_workflow(
                repo_root=repo_root,
                registry_path=registry_path,
                candidate_dir=Path(init_payload["candidateDir"]),
                source_files=source_files,
                output_path=out_path,
            )
            if output_error:
                failures.append(f"{candidate_id}: {output_error}")
            failures.extend(f"{candidate_id}: {failure}" for failure in command_errors(run))
            failures.extend(
                f"{candidate_id}: {failure}"
                for failure in validate_workflow_dossier(
                    dossier,
                    expected_mode="existing_candidate_dir",
                    expected_validator=SHAPE_ONLY_VALIDATOR_VERDICT,
                    expected_review=SHAPE_ONLY_REVIEW_VERDICT,
                    expected_source_count=1,
                )
            )
            if isinstance(dossier, dict):
                dossiers.append(dossier)
                compact.append(workflow_compact_summary(dossier))
                if index == 0:
                    output_verification = {
                        "checked": True,
                        "mode": "existing_candidate_dir",
                        "path": str(output_path),
                        "schemaMatched": not dossier_schema_failures(dossier),
                        "status": dossier.get("status"),
                    }

        details = {
            "summary": summarize_control_dossiers(dossiers),
            "candidateSummaries": compact,
            "outputFileVerification": output_verification,
        }
        return make_subtest(
            "shape_only_existing_candidate_controls",
            failures=failures,
            details=details,
            candidate_count=len(dossiers),
            expected_count=len(family_ids),
        ), output_verification


def run_multi_source_verification(
    *,
    repo_root: Path,
    registry_path: Path,
    family_ids: list[str],
) -> dict[str, Any]:
    family_id = family_ids[0]
    slug = family_slug(family_id)
    candidate_id = f"workflow_multi_source_{slug}"
    with tempfile.TemporaryDirectory(prefix="popker_source_drop_multi_") as temp_name:
        temp_root = Path(temp_name)
        source_files = make_source_files(temp_root, candidate_id, 2)
        dossier, run, output_error = run_workflow(
            repo_root=repo_root,
            registry_path=registry_path,
            family_id=family_id,
            candidate_id=candidate_id,
            staging_root=temp_root / "staging",
            source_files=source_files,
        )
        failures: list[str] = []
        if output_error:
            failures.append(output_error)
        failures.extend(command_errors(run))
        failures.extend(
            validate_workflow_dossier(
                dossier,
                expected_mode="scaffold_new",
                expected_validator=TEMPLATE_VALIDATOR_VERDICT,
                expected_review=TEMPLATE_REVIEW_VERDICT,
                expected_source_count=2,
            )
        )
        compact = workflow_compact_summary(dossier)
        expected_paths = ["source/retained_source_01.txt", "source/retained_source_02.txt"]
        if compact.get("retainedPaths") != expected_paths:
            failures.append(f"retainedPaths expected={expected_paths} actual={compact.get('retainedPaths')}")
        if compact.get("copiedSourceIndexes") != [0, 1]:
            failures.append(f"copiedSourceIndexes expected=[0, 1] actual={compact.get('copiedSourceIndexes')}")
        manifest_fields = set(compact.get("manifestFieldsTouched", []))
        metadata_fields = set(compact.get("metadataFieldsTouched", []))
        required_manifest = {"currentRepoStatus", "nonGroundingReason", "provenance.seededRetainedSources"}
        required_metadata = {"candidateStatus", "currentRepoStatus", "nonGroundingReason", "seededSourceSummary", "templateStatus"}
        if not required_manifest.issubset(manifest_fields):
            failures.append(f"manifestFieldsTouched_missing={sorted(required_manifest - manifest_fields)}")
        if not required_metadata.issubset(metadata_fields):
            failures.append(f"metadataFieldsTouched_missing={sorted(required_metadata - metadata_fields)}")

        return make_subtest(
            "multi_source_scaffold_new_verification",
            failures=failures,
            details={
                "candidateId": candidate_id,
                "familyId": family_id,
                "copiedSourceCount": compact.get("copiedSourceCount"),
                "retainedPaths": compact.get("retainedPaths"),
                "copiedSourceIndexes": compact.get("copiedSourceIndexes"),
                "manifestFieldsTouched": compact.get("manifestFieldsTouched"),
                "metadataFieldsTouched": compact.get("metadataFieldsTouched"),
                "validatorVerdict": compact.get("validatorVerdict"),
                "reviewVerdict": compact.get("reviewVerdict"),
            },
            candidate_count=1 if isinstance(dossier, dict) else 0,
            expected_count=1,
        )


def workflow_fail_closed_run(
    *,
    repo_root: Path,
    args: list[str],
) -> dict[str, Any]:
    return run_command([sys.executable, "scripts/run_mix_game_source_drop_workflow.py", *args], repo_root=repo_root)


def fail_closed_result(name: str, run: dict[str, Any], expected_fragment: str) -> dict[str, Any]:
    payload = run.get("stdoutJson") if isinstance(run.get("stdoutJson"), dict) else {}
    execution_errors = payload.get("executionErrors", []) if isinstance(payload, dict) else []
    error_strings = [str(error) for error in execution_errors]
    matched = any(expected_fragment in error for error in error_strings)
    failures: list[str] = []
    if run["exitCode"] == 0:
        failures.append("expected_nonzero_exit")
    if not isinstance(payload, dict):
        failures.append("expected_parseable_json_dossier")
    elif payload.get("status") != "failed":
        failures.append(f"expected_status_failed actual={payload.get('status')}")
    if not matched:
        failures.append(f"expected_error_fragment_not_found: {expected_fragment}")
    if run.get("stdoutJsonError"):
        failures.append(str(run["stdoutJsonError"]))

    return make_subtest(
        name,
        failures=failures,
        details={
            "expectedErrorFragment": expected_fragment,
            "matchedExpectedError": matched,
            "exitCode": run["exitCode"],
            "status": payload.get("status") if isinstance(payload, dict) else None,
            "executionErrors": execution_errors,
        },
        expected_fail_closed=True,
    )


def run_fail_closed_checks(
    *,
    repo_root: Path,
    registry_path: Path,
    family_ids: list[str],
) -> list[dict[str, Any]]:
    family_id = family_ids[0]
    slug = family_slug(family_id)
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="popker_source_drop_failclosed_") as temp_name:
        temp_root = Path(temp_name)
        source_file = make_source_files(temp_root, "fail_closed_valid_source", 1)[0]

        missing_mode_run = workflow_fail_closed_run(
            repo_root=repo_root,
            args=["--registry", str(registry_path), "--source-file", str(source_file)],
        )
        results.append(fail_closed_result("fail_closed_missing_mode_selection", missing_mode_run, "missing_mode_selection"))

        conflicting_dir = temp_root / slug / "fail_conflicting_mode"
        conflicting_run = workflow_fail_closed_run(
            repo_root=repo_root,
            args=[
                "--registry",
                str(registry_path),
                "--candidate-dir",
                str(conflicting_dir),
                "--family",
                family_id,
                "--candidate-id",
                "fail_conflicting_mode",
                "--staging-root",
                str(temp_root / "staging"),
                "--source-file",
                str(source_file),
            ],
        )
        results.append(fail_closed_result("fail_closed_conflicting_mode_selection", conflicting_run, "conflicting_mode_selection"))

        missing_source_run = workflow_fail_closed_run(
            repo_root=repo_root,
            args=[
                "--registry",
                str(registry_path),
                "--family",
                family_id,
                "--candidate-id",
                "fail_missing_source",
                "--staging-root",
                str(temp_root / "missing_source_staging"),
                "--source-file",
                str(temp_root / "no_such_source.txt"),
            ],
        )
        results.append(fail_closed_result("fail_closed_missing_source_file", missing_source_run, "source_file_not_found_or_not_file"))

        missing_candidate_dir_run = workflow_fail_closed_run(
            repo_root=repo_root,
            args=[
                "--registry",
                str(registry_path),
                "--candidate-dir",
                str(temp_root / "no_such_candidate_dir"),
                "--source-file",
                str(source_file),
            ],
        )
        results.append(fail_closed_result("fail_closed_missing_candidate_dir", missing_candidate_dir_run, "candidate_dir_not_found"))

        missing_json_dir = temp_root / slug / "fail_missing_candidate_json"
        missing_json_dir.mkdir(parents=True)
        missing_candidate_json_run = workflow_fail_closed_run(
            repo_root=repo_root,
            args=[
                "--registry",
                str(registry_path),
                "--candidate-dir",
                str(missing_json_dir),
                "--source-file",
                str(source_file),
            ],
        )
        results.append(fail_closed_result("fail_closed_missing_candidate_json", missing_candidate_json_run, "missing candidate.json"))

    return results


def summarize_subtests(subtests: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [subtest for subtest in subtests if subtest.get("status") != "passed"]
    expected_fail_closed = [subtest for subtest in subtests if subtest.get("expectedFailClosed")]
    template_summary = next(
        (item.get("details", {}).get("summary", {}) for item in subtests if item.get("name") == "template_mode_scaffold_new_controls"),
        {},
    )
    shape_summary = next(
        (item.get("details", {}).get("summary", {}) for item in subtests if item.get("name") == "shape_only_existing_candidate_controls"),
        {},
    )
    multi_source = next(
        (item.get("details", {}) for item in subtests if item.get("name") == "multi_source_scaffold_new_verification"),
        {},
    )
    output_checks = []
    for item in subtests:
        output_check = item.get("details", {}).get("outputFileVerification")
        if isinstance(output_check, dict) and output_check.get("checked"):
            output_checks.append(output_check)
    return {
        "subtestsTotal": len(subtests),
        "subtestsPassed": len(subtests) - len(failed),
        "subtestsFailed": len(failed),
        "failingSubtests": [str(item.get("name")) for item in failed],
        "templateModeCandidates": template_summary.get("totalCandidates", 0),
        "shapeOnlyModeCandidates": shape_summary.get("totalCandidates", 0),
        "multiSourceCopiedSourceCount": multi_source.get("copiedSourceCount"),
        "outputFileChecksPassed": sum(1 for item in output_checks if item.get("schemaMatched") and item.get("status") == "ok"),
        "expectedFailClosedErrorCount": len(expected_fail_closed),
        "unexpectedExecutionErrorCount": sum(int(item.get("executionErrorCount") or 0) for item in failed),
        "falsePositiveRiskCount": int(template_summary.get("falsePositiveRiskCount") or 0)
        + int(shape_summary.get("falsePositiveRiskCount") or 0),
        "promotionCandidatePendingHumanReviewCount": int(template_summary.get("promotionCandidatePendingHumanReviewCount") or 0)
        + int(shape_summary.get("promotionCandidatePendingHumanReviewCount") or 0),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=REGISTRY_REL,
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
    family_ids = family_ids_from_registry(registry)
    if not family_ids:
        payload = {
            "sourceDropWorkflowRegressionVersion": REGRESSION_VERSION,
            "repoRoot": str(repo_root),
            "registryPath": str(registry_path),
            "status": "passed",
            "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
            "familyIds": [],
            "requiredDossierKeys": REQUIRED_DOSSIER_KEYS,
            "coverageLimits": [
                "No blocked families remain in the current registry boundary, so blocked-family source-drop workflow regression is not exercised in this pass."
            ],
            "toolsReused": [
                "scripts/run_mix_game_source_drop_workflow.py",
                "scripts/init_mix_game_shape_only_candidates.py",
                "scripts/seed_mix_game_candidate_sources.py",
                "scripts/run_mix_game_candidate_intake.py",
            ],
            "existingScriptsExtended": [],
            "outputFileVerification": {
                "checks": [],
                "passed": True,
            },
            "summary": {
                "templateModeCandidates": 0,
                "shapeOnlyModeCandidates": 0,
                "multiSourceCopiedSourceCount": 0,
                "outputFileChecksPassed": 0,
                "expectedFailClosedErrorCount": 0,
                "unexpectedExecutionErrorCount": 0,
                "falsePositiveRiskCount": 0,
                "promotionCandidatePendingHumanReviewCount": 0,
                "subtestsTotal": 0,
                "subtestsPassed": 0,
                "subtestsFailed": 0,
                "failingSubtests": [],
                "failingCandidateIds": [],
            },
            "subtests": [],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    template_subtest, template_output_check = run_template_mode_controls(
        repo_root=repo_root,
        registry_path=registry_path,
        family_ids=family_ids,
    )
    shape_subtest, shape_output_check = run_shape_only_mode_controls(
        repo_root=repo_root,
        registry_path=registry_path,
        family_ids=family_ids,
    )
    multi_source_subtest = run_multi_source_verification(
        repo_root=repo_root,
        registry_path=registry_path,
        family_ids=family_ids,
    )
    fail_closed_subtests = run_fail_closed_checks(
        repo_root=repo_root,
        registry_path=registry_path,
        family_ids=family_ids,
    )

    subtests = [template_subtest, shape_subtest, multi_source_subtest, *fail_closed_subtests]
    summary = summarize_subtests(subtests)
    status = "passed" if summary["subtestsFailed"] == 0 else "failed"
    payload = {
        "sourceDropWorkflowRegressionVersion": REGRESSION_VERSION,
        "repoRoot": str(repo_root),
        "registryPath": str(registry_path),
        "status": status,
        "currentGroundingBoundary": registry.get("currentGroundingBoundary", {}),
        "familyIds": family_ids,
        "requiredDossierKeys": REQUIRED_DOSSIER_KEYS,
        "coverageLimits": COVERAGE_LIMITS,
        "toolsReused": [
            "scripts/run_mix_game_source_drop_workflow.py",
            "scripts/init_mix_game_shape_only_candidates.py",
            "scripts/seed_mix_game_candidate_sources.py",
            "scripts/run_mix_game_candidate_intake.py",
        ],
        "existingScriptsExtended": [],
        "outputFileVerification": {
            "checks": [template_output_check, shape_output_check],
            "passed": all(
                item.get("checked") and item.get("schemaMatched") and item.get("status") == "ok"
                for item in [template_output_check, shape_output_check]
            ),
        },
        "summary": summary,
        "subtests": subtests,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
