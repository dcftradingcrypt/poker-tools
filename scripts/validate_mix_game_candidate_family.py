#!/usr/bin/env python3
"""Validate blocked-family candidate pack/manifest pairs against repo-local intake contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MISSING = object()


def get_default_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "out" / "_codex" / "mix_game_family_contract_registry.json"


def load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return None, f"file_not_found: {path}"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: {path}: line={exc.lineno} col={exc.colno} msg={exc.msg}"
    except OSError as exc:
        return None, f"os_error: {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"root_not_object: {path}"
    return data, None


def get_path(obj: Any, path: str) -> Any:
    current = obj
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return MISSING
    return current


def value_is_non_empty(value: Any) -> bool:
    if value is MISSING or value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def is_placeholder_string(value: Any, prefixes: list[str]) -> bool:
    return isinstance(value, str) and any(value.startswith(prefix) for prefix in prefixes)


def iter_string_paths(obj: Any, prefix: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_prefix = f"{prefix}.{key}" if prefix else key
            out.extend(iter_string_paths(value, next_prefix))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            next_prefix = f"{prefix}[{index}]"
            out.extend(iter_string_paths(value, next_prefix))
    elif isinstance(obj, str):
        out.append((prefix, obj))
    return out


def find_transformation_stage(manifest: dict[str, Any], stage_name: str) -> Any:
    chain = get_path(manifest, "provenance.transformationChain")
    if not isinstance(chain, list):
        return MISSING
    for item in chain:
        if isinstance(item, dict) and item.get("stage") == stage_name:
            return item
    return MISSING


def add_result(target: dict[str, list[Any]], key: str, value: Any) -> None:
    target.setdefault(key, []).append(value)


def evaluate_literal_paths(
    obj: dict[str, Any],
    rules: list[dict[str, Any]],
    category: str,
    matched: dict[str, list[Any]],
    wrong_family: list[dict[str, Any]],
) -> None:
    for rule in rules:
        path = rule["path"]
        expected = rule["expected"]
        actual = get_path(obj, path)
        if actual == expected:
            add_result(matched, category, {"path": path, "expected": expected})
            continue
        wrong_family.append(
            {
                "category": category,
                "path": path,
                "expected": expected,
                "actual": None if actual is MISSING else actual,
            }
        )


def evaluate_non_empty_paths(
    obj: dict[str, Any],
    paths: list[str],
    category: str,
    matched: dict[str, list[Any]],
    missing: dict[str, list[Any]],
) -> None:
    for path in paths:
        actual = get_path(obj, path)
        if value_is_non_empty(actual):
            add_result(matched, category, {"path": path})
        else:
            add_result(missing, category, {"path": path, "actual": None if actual is MISSING else actual})


def evaluate_candidate_ranges(
    pack: dict[str, Any],
    required_node_keys: list[str],
    required_entry_keys: list[str],
    matched: dict[str, list[Any]],
    missing: dict[str, list[Any]],
) -> None:
    candidate_ranges = get_path(pack, "candidateRanges")
    if not isinstance(candidate_ranges, list) or not candidate_ranges:
        add_result(missing, "packCandidateRanges", {"path": "candidateRanges", "actual": None if candidate_ranges is MISSING else candidate_ranges})
        return
    add_result(matched, "packCandidateRanges", {"path": "candidateRanges", "count": len(candidate_ranges)})
    for node_index, node in enumerate(candidate_ranges):
        if not isinstance(node, dict):
            add_result(missing, "packNodeKeys", {"nodeIndex": node_index, "path": f"candidateRanges[{node_index}]", "actual": node})
            continue
        for key in required_node_keys:
            if key in node:
                add_result(matched, "packNodeKeys", {"nodeIndex": node_index, "key": key})
            else:
                add_result(missing, "packNodeKeys", {"nodeIndex": node_index, "key": key})
        entries = node.get("entries")
        if not isinstance(entries, list) or not entries:
            add_result(missing, "packEntryKeys", {"nodeIndex": node_index, "path": f"candidateRanges[{node_index}].entries", "actual": entries})
            continue
        for entry_index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                add_result(missing, "packEntryKeys", {"nodeIndex": node_index, "entryIndex": entry_index, "actual": entry})
                continue
            for key in required_entry_keys:
                if key in entry:
                    add_result(matched, "packEntryKeys", {"nodeIndex": node_index, "entryIndex": entry_index, "key": key})
                else:
                    add_result(missing, "packEntryKeys", {"nodeIndex": node_index, "entryIndex": entry_index, "key": key})


def evaluate_transformation_stages(
    manifest: dict[str, Any],
    required_stages: list[str],
    matched: dict[str, list[Any]],
    missing: dict[str, list[Any]],
) -> None:
    for stage_name in required_stages:
        stage = find_transformation_stage(manifest, stage_name)
        if stage is MISSING:
            add_result(missing, "manifestTransformationStages", {"stage": stage_name})
        else:
            add_result(matched, "manifestTransformationStages", {"stage": stage_name})


def evaluate_collisions(
    pack: dict[str, Any],
    manifest: dict[str, Any],
    common_rules: list[dict[str, Any]],
    family_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    collisions: list[dict[str, Any]] = []

    def maybe_add(scope_name: str, rule: dict[str, Any], actual: Any, evidence: Any = None) -> None:
        collisions.append(
            {
                "id": rule["id"],
                "scope": scope_name,
                "reason": rule["reason"],
                "path": rule.get("path"),
                "actual": actual,
                "evidence": evidence,
            }
        )

    for rule in [*common_rules, *family_rules]:
        target = pack if rule["scope"] == "pack" else manifest
        kind = rule["kind"]
        if kind == "path_present":
            actual = get_path(target, rule["path"])
            if actual is not MISSING:
                maybe_add(rule["scope"], rule, actual)
        elif kind == "path_equals":
            actual = get_path(target, rule["path"])
            if actual is not MISSING and actual == rule["expectedValue"]:
                maybe_add(rule["scope"], rule, actual)
        elif kind == "path_in":
            actual = get_path(target, rule["path"])
            if actual is not MISSING and actual in rule["expectedValues"]:
                maybe_add(rule["scope"], rule, actual)
        elif kind == "any_string_contains":
            matches = [
                {"path": path, "value": value}
                for path, value in iter_string_paths(target)
                if rule["needle"] in value
            ]
            if matches:
                maybe_add(rule["scope"], rule, rule["needle"], matches)
    return collisions


def evaluate_provenance_gaps(
    manifest: dict[str, Any],
    provenance_rules: dict[str, Any],
    shared_rules: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    prefixes = shared_rules["placeholderStringPrefixes"]

    for path in provenance_rules["requiredSourceFields"] + provenance_rules["requiredArtifactFields"] + provenance_rules["requiredProvenanceFields"]:
        actual = get_path(manifest, path)
        if not value_is_non_empty(actual):
            gaps.append({"path": path, "issue": "missing_or_empty", "actual": None if actual is MISSING else actual})
        elif is_placeholder_string(actual, prefixes):
            gaps.append({"path": path, "issue": "placeholder_value", "actual": actual})

    for stage_name in provenance_rules["requiredTransformationStages"]:
        stage = find_transformation_stage(manifest, stage_name)
        if stage is MISSING:
            gaps.append({"path": "provenance.transformationChain", "issue": "missing_stage", "stage": stage_name})
            continue
        if not isinstance(stage, dict):
            gaps.append({"path": "provenance.transformationChain", "issue": "invalid_stage_shape", "stage": stage_name, "actual": stage})
            continue
        path_value = stage.get("path", MISSING)
        if not value_is_non_empty(path_value):
            gaps.append({"path": f"provenance.transformationChain[{stage_name}].path", "issue": "missing_or_empty", "actual": None if path_value is MISSING else path_value})
        elif is_placeholder_string(path_value, prefixes):
            gaps.append({"path": f"provenance.transformationChain[{stage_name}].path", "issue": "placeholder_value", "actual": path_value})
        if stage_name == "retained_source_basis":
            linkage_value = stage.get("sha256OrEquivalentLinkage", MISSING)
            if not value_is_non_empty(linkage_value):
                gaps.append({"path": f"provenance.transformationChain[{stage_name}].sha256OrEquivalentLinkage", "issue": "missing_or_empty", "actual": None if linkage_value is MISSING else linkage_value})
            elif is_placeholder_string(linkage_value, prefixes):
                gaps.append({"path": f"provenance.transformationChain[{stage_name}].sha256OrEquivalentLinkage", "issue": "placeholder_value", "actual": linkage_value})
        else:
            hash_value = stage.get("sha256", MISSING)
            if not value_is_non_empty(hash_value):
                gaps.append({"path": f"provenance.transformationChain[{stage_name}].sha256", "issue": "missing_or_empty", "actual": None if hash_value is MISSING else hash_value})
            elif is_placeholder_string(hash_value, prefixes):
                gaps.append({"path": f"provenance.transformationChain[{stage_name}].sha256", "issue": "placeholder_value", "actual": hash_value})
    return gaps


def determine_status_blockers(
    pack: dict[str, Any],
    manifest: dict[str, Any],
    shared_rules: dict[str, Any],
    provenance_gaps: list[dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    template_status = shared_rules["templateStatusMatch"]
    if get_path(pack, "templateStatus") == template_status:
        blockers.append("pack.templateStatus remains candidate_non_grounding")
    if get_path(manifest, "templateStatus") == template_status:
        blockers.append("manifest.templateStatus remains candidate_non_grounding")
    if provenance_gaps:
        blockers.append("manifest provenance is incomplete, placeholder-bearing, or both")
    return blockers


def template_match(pack: dict[str, Any], manifest: dict[str, Any], shared_rules: dict[str, Any]) -> bool:
    return (
        get_path(pack, "templateStatus") == shared_rules["templateStatusMatch"]
        and get_path(manifest, "templateStatus") == shared_rules["templateStatusMatch"]
        and get_path(pack, "currentRepoStatus") == shared_rules["blockedStatusMatch"]
        and get_path(manifest, "currentRepoStatus") == shared_rules["blockedStatusMatch"]
    )


def count_issues(bucket: dict[str, list[Any]]) -> int:
    return sum(len(values) for values in bucket.values())


def validate_candidate(
    registry: dict[str, Any],
    family_id: str,
    pack_path: Path,
    manifest_path: Path,
    registry_path: Path,
) -> dict[str, Any]:
    pack, pack_error = load_json_object(pack_path)
    manifest, manifest_error = load_json_object(manifest_path)

    if pack_error or manifest_error:
        return {
            "validatorVersion": "1.0",
            "familyId": family_id,
            "currentRegistryStatus": "blocked_no_source",
            "registryPath": str(registry_path),
            "packPath": str(pack_path),
            "manifestPath": str(manifest_path),
            "verdict": "invalid_candidate_json",
            "matchedMarkers": {},
            "wrongFamilyMarkers": [],
            "missingMarkers": {},
            "excludedAssumptionCollisions": [],
            "provenanceGaps": [],
            "statusBlockers": [],
            "errors": [error for error in [pack_error, manifest_error] if error],
        }

    family_rule = next((entry for entry in registry["families"] if entry["familyId"] == family_id), None)
    if family_rule is None:
        raise ValueError(f"unknown family id: {family_id}")

    shared_rules = registry["sharedValidationRules"]
    matched: dict[str, list[Any]] = {}
    wrong_family: list[dict[str, Any]] = []
    missing: dict[str, list[Any]] = {}

    evaluate_literal_paths(pack, family_rule["minimumPayloadMarkers"]["packRequiredLiteralPaths"], "packLiteralPaths", matched, wrong_family)
    evaluate_literal_paths(manifest, family_rule["minimumPayloadMarkers"]["manifestRequiredLiteralPaths"], "manifestLiteralPaths", matched, wrong_family)

    evaluate_non_empty_paths(
        pack,
        shared_rules["commonPackNonEmptyPaths"] + family_rule["minimumPayloadMarkers"]["packRequiredNonEmptyPaths"],
        "packNonEmptyPaths",
        matched,
        missing,
    )
    evaluate_non_empty_paths(
        manifest,
        shared_rules["commonManifestNonEmptyPaths"] + family_rule["minimumPayloadMarkers"]["manifestRequiredNonEmptyPaths"],
        "manifestNonEmptyPaths",
        matched,
        missing,
    )
    evaluate_candidate_ranges(
        pack,
        family_rule["minimumPayloadMarkers"]["packRequiredNodeKeys"],
        family_rule["minimumPayloadMarkers"]["packRequiredEntryKeys"],
        matched,
        missing,
    )
    evaluate_transformation_stages(manifest, family_rule["minimumRetainedProvenance"]["requiredTransformationStages"], matched, missing)

    collisions = evaluate_collisions(
        pack,
        manifest,
        shared_rules["commonExcludedCollisionRules"],
        family_rule["excludedCollisionRules"],
    )
    provenance_gaps = evaluate_provenance_gaps(manifest, family_rule["minimumRetainedProvenance"], shared_rules)
    status_blockers = determine_status_blockers(pack, manifest, shared_rules, provenance_gaps)

    if wrong_family:
        verdict = "rejected_wrong_family_markers"
    elif collisions:
        verdict = "rejected_excluded_inherited_assumptions"
    elif count_issues(missing) > 0:
        verdict = "rejected_missing_required_markers_or_provenance"
    elif template_match(pack, manifest, shared_rules):
        verdict = "candidate_non_grounding_template_match"
    elif provenance_gaps or status_blockers:
        verdict = "shape_match_missing_grounding_evidence"
    else:
        verdict = "shape_match_with_grounding_evidence_candidate"

    return {
        "validatorVersion": "1.0",
        "familyId": family_id,
        "currentRegistryStatus": family_rule["currentRepoStatus"],
        "registryPath": str(registry_path),
        "packPath": str(pack_path),
        "manifestPath": str(manifest_path),
        "verdict": verdict,
        "matchedMarkers": matched,
        "wrongFamilyMarkers": wrong_family,
        "missingMarkers": missing,
        "excludedAssumptionCollisions": collisions,
        "provenanceGaps": provenance_gaps,
        "statusBlockers": status_blockers,
        "promotionAcceptanceChecks": family_rule["promotionAcceptanceChecks"],
        "templatePaths": family_rule["templatePaths"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True, help="Blocked family id to validate against.")
    parser.add_argument("--pack", required=True, help="Candidate pack JSON path.")
    parser.add_argument("--manifest", required=True, help="Candidate manifest JSON path.")
    parser.add_argument(
        "--registry",
        default=str(get_default_registry_path()),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry_path = Path(args.registry)
    registry, registry_error = load_json_object(registry_path)
    if registry_error:
        payload = {
            "validatorVersion": "1.0",
            "familyId": args.family,
            "registryPath": str(registry_path),
            "packPath": args.pack,
            "manifestPath": args.manifest,
            "verdict": "invalid_candidate_json",
            "errors": [registry_error],
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    try:
        result = validate_candidate(registry, args.family, Path(args.pack), Path(args.manifest), registry_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
