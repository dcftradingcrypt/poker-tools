#!/usr/bin/env python3
"""Batch wrapper for blocked-family candidate pack/manifest validation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_family import (
    get_default_registry_path,
    load_json_object,
    validate_candidate,
)


BATCH_VALIDATOR_VERSION = "1.0"
INVALID_VERDICT = "invalid_candidate_json"
REQUIRED_CANDIDATE_FIELDS = ("candidateId", "familyId", "packPath", "manifestPath")


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def count_bucket(bucket: Any) -> int:
    if not isinstance(bucket, dict):
        return 0
    return sum(len(values) for values in bucket.values() if isinstance(values, list))


def load_batch_spec(path_arg: str) -> tuple[dict[str, Any] | None, str | None, Path | None]:
    if path_arg == "-":
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            return None, f"json_decode_error: <stdin>: line={exc.lineno} col={exc.colno} msg={exc.msg}", None
        if not isinstance(data, dict):
            return None, "root_not_object: <stdin>", None
        return data, None, None

    path = Path(path_arg)
    if not path.is_absolute():
        path = Path.cwd() / path
    data, error = load_json_object(path)
    return data, error, path


def resolve_registry_path(path_arg: str, repo_root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return repo_root / path


def get_path_base(spec: dict[str, Any], spec_path: Path | None, repo_root: Path) -> tuple[Path | None, str | None]:
    path_base = spec.get("pathBase", "repo_root")
    if path_base == "repo_root":
        return repo_root, None
    if path_base == "batch_spec_dir":
        if spec_path is None:
            return None, "pathBase=batch_spec_dir is unavailable when --batch-spec is read from stdin"
        return spec_path.parent, None
    return None, f"unsupported pathBase: {path_base}"


def resolve_candidate_path(path_value: str, base_path: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return base_path / path


def validate_candidate_entry_shape(entry: Any, index: int) -> list[str]:
    if not isinstance(entry, dict):
        return [f"candidate[{index}] root_not_object"]

    errors: list[str] = []
    for field in REQUIRED_CANDIDATE_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"candidate[{index}].{field} missing_or_not_nonempty_string")

    expected = entry.get("expectedVerdict")
    if "expectedVerdict" in entry and expected is not None and not isinstance(expected, str):
        errors.append(f"candidate[{index}].expectedVerdict not_string_or_null")
    return errors


def make_error_result(entry: Any, index: int, errors: list[str]) -> dict[str, Any]:
    safe_entry = entry if isinstance(entry, dict) else {}
    expected = safe_entry.get("expectedVerdict")
    expected_matched = False if isinstance(expected, str) else None
    return {
        "candidateId": safe_entry.get("candidateId", f"<candidate-{index}>"),
        "familyId": safe_entry.get("familyId"),
        "packPath": safe_entry.get("packPath"),
        "manifestPath": safe_entry.get("manifestPath"),
        "notes": safe_entry.get("notes"),
        "expectedVerdict": expected,
        "expectedVerdictMatched": expected_matched,
        "verdict": INVALID_VERDICT,
        "issueCounts": {
            "wrongFamilyMarkers": 0,
            "missingMarkers": 0,
            "excludedAssumptionCollisions": 0,
            "provenanceGaps": 0,
            "statusBlockers": 0,
            "validatorErrors": 0,
        },
        "executionErrors": errors,
    }


def summarize_validation_output(validation: dict[str, Any]) -> dict[str, int]:
    return {
        "wrongFamilyMarkers": len(validation.get("wrongFamilyMarkers", [])),
        "missingMarkers": count_bucket(validation.get("missingMarkers", {})),
        "excludedAssumptionCollisions": len(validation.get("excludedAssumptionCollisions", [])),
        "provenanceGaps": len(validation.get("provenanceGaps", [])),
        "statusBlockers": len(validation.get("statusBlockers", [])),
        "validatorErrors": len(validation.get("errors", [])),
    }


def build_candidate_result(
    entry: dict[str, Any],
    index: int,
    registry: dict[str, Any],
    registry_path: Path,
    path_base: Path,
) -> dict[str, Any]:
    shape_errors = validate_candidate_entry_shape(entry, index)
    if shape_errors:
        return make_error_result(entry, index, shape_errors)

    candidate_id = entry["candidateId"]
    family_id = entry["familyId"]
    pack_path = resolve_candidate_path(entry["packPath"], path_base)
    manifest_path = resolve_candidate_path(entry["manifestPath"], path_base)
    expected = entry.get("expectedVerdict")

    try:
        validation = validate_candidate(registry, family_id, pack_path, manifest_path, registry_path)
    except ValueError as exc:
        return make_error_result(entry, index, [str(exc)])

    verdict = validation["verdict"]
    return {
        "candidateId": candidate_id,
        "familyId": family_id,
        "packPath": entry["packPath"],
        "manifestPath": entry["manifestPath"],
        "resolvedPackPath": str(pack_path),
        "resolvedManifestPath": str(manifest_path),
        "notes": entry.get("notes"),
        "expectedVerdict": expected,
        "expectedVerdictMatched": (verdict == expected) if isinstance(expected, str) else None,
        "verdict": verdict,
        "issueCounts": summarize_validation_output(validation),
        "executionErrors": validation.get("errors", []),
    }


def build_payload(
    *,
    batch_spec_path: str,
    registry_path: Path,
    batch_id: Any = None,
    path_base_label: Any = None,
    status: str,
    results: list[dict[str, Any]],
    execution_errors: list[Any],
) -> dict[str, Any]:
    by_verdict = Counter(result.get("verdict", INVALID_VERDICT) for result in results)
    expected_matches = sum(1 for result in results if result.get("expectedVerdictMatched") is True)
    expected_mismatches = sum(1 for result in results if result.get("expectedVerdictMatched") is False)
    expected_missing = sum(1 for result in results if result.get("expectedVerdictMatched") is None)
    candidate_error_count = sum(len(result.get("executionErrors", [])) for result in results)
    summary = {
        "totalCandidates": len(results),
        "byVerdict": dict(sorted(by_verdict.items())),
        "expectedVerdictMatches": expected_matches,
        "expectedVerdictMismatches": expected_mismatches,
        "expectedVerdictNotProvided": expected_missing,
        "executionErrorCount": candidate_error_count + len(execution_errors),
    }
    return {
        "batchValidatorVersion": BATCH_VALIDATOR_VERSION,
        "batchSpecPath": batch_spec_path,
        "registryPath": str(registry_path),
        "batchId": batch_id,
        "pathBase": path_base_label,
        "status": status,
        "summary": summary,
        "executionErrors": execution_errors,
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-spec", required=True, help="Batch spec JSON path, or '-' to read from stdin.")
    parser.add_argument(
        "--registry",
        default=str(get_default_registry_path()),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_registry_path(args.registry, repo_root)

    spec, spec_error, resolved_spec_path = load_batch_spec(args.batch_spec)
    if spec_error or spec is None:
        payload = build_payload(
            batch_spec_path=args.batch_spec,
            registry_path=registry_path,
            status="invalid_batch_spec",
            results=[],
            execution_errors=[spec_error or "unknown_batch_spec_error"],
        )
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    registry, registry_error = load_json_object(registry_path)
    if registry_error or registry is None:
        payload = build_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_registry",
            results=[],
            execution_errors=[registry_error or "unknown_registry_error"],
        )
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    candidates = spec.get("candidates")
    if not isinstance(candidates, list):
        payload = build_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_batch_spec",
            results=[],
            execution_errors=["candidates missing_or_not_list"],
        )
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    path_base, path_base_error = get_path_base(spec, resolved_spec_path, repo_root)
    if path_base_error or path_base is None:
        payload = build_payload(
            batch_spec_path=str(resolved_spec_path or args.batch_spec),
            registry_path=registry_path,
            batch_id=spec.get("batchId"),
            path_base_label=spec.get("pathBase", "repo_root"),
            status="invalid_batch_spec",
            results=[],
            execution_errors=[path_base_error or "unknown_path_base_error"],
        )
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    results = [
        build_candidate_result(entry, index, registry, registry_path, path_base)
        for index, entry in enumerate(candidates)
    ]
    execution_errors = [
        {"candidateId": result.get("candidateId"), "errors": result.get("executionErrors", [])}
        for result in results
        if result.get("executionErrors")
    ]
    if execution_errors:
        status = "completed_with_errors"
    elif any(result.get("expectedVerdictMatched") is False for result in results):
        status = "completed_with_expected_verdict_mismatches"
    else:
        status = "ok"

    payload = build_payload(
        batch_spec_path=str(resolved_spec_path or args.batch_spec),
        registry_path=registry_path,
        batch_id=spec.get("batchId"),
        path_base_label=spec.get("pathBase", "repo_root"),
        status=status,
        results=results,
        execution_errors=execution_errors,
    )
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
