#!/usr/bin/env python3
"""Initialize synthetic shape-only blocked-family candidates from repo-local templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_family import get_default_registry_path, load_json_object


SHAPE_FIXTURE_VERSION = "1.0"
SYNTHETIC_STATUS = "synthetic_shape_only_non_grounding"
DEFAULT_EXPECTED_VERDICT = "shape_match_missing_grounding_evidence"
SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def family_slug(family_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", family_id.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def resolve_repo_path(path_arg: str, repo_root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return repo_root / path


def load_registry(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    registry, error = load_json_object(path)
    if error:
        return None, error
    if not isinstance(registry.get("families"), list):
        return None, "registry.families missing_or_not_list"
    return registry, None


def find_family(registry: dict[str, Any], family_id: str) -> dict[str, Any] | None:
    return next((entry for entry in registry["families"] if entry.get("familyId") == family_id), None)


def validate_candidate_id(candidate_id: str) -> str | None:
    if not SAFE_SEGMENT_RE.fullmatch(candidate_id):
        return "candidate_id must match ^[A-Za-z0-9][A-Za-z0-9._-]*$"
    return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_path(obj: Any, path: str) -> Any:
    current = obj
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def set_path(obj: dict[str, Any], path: str, value: Any) -> None:
    current = obj
    parts = path.split(".")
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = value


def value_is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (dict, list)):
        return len(value) > 0
    return True


def is_template_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(("<required-", "<optional-", "<populate-on-generation>"))


def synthetic_value_for_key(key: str, family_id: str, slug: str) -> Any:
    values: dict[str, Any] = {
        "actingOrderState": "synthetic_acting_order_state",
        "actingSeatOrOrder": "synthetic_acting_seat_or_order",
        "actingSeatOrRole": "synthetic_acting_seat_or_role",
        "bettingModel": "synthetic_betting_model",
        "bringInModel": "synthetic_bring_in_model",
        "deadCardModel": "synthetic_dead_card_model",
        "decisionNodeId": f"synthetic_{slug}_node_001",
        "doorCardContext": "synthetic_door_card_context",
        "drawRound": "synthetic_draw_round",
        "effectiveStackBandOrSpr": "synthetic_effective_stack_or_spr_band",
        "facingAction": "synthetic_facing_action",
        "gameForm": "synthetic_family_shape_fixture",
        "handToken": f"SYNTHETIC_{slug.upper()}_HAND_TOKEN",
        "license": "synthetic_fixture_not_source_license",
        "lowDirectionRule": "ace_to_five",
        "lowQualifierRule": "synthetic_low_qualifier_rule",
        "lowSystem": "synthetic_low_system",
        "name": f"synthetic shape-only fixture for {family_id}",
        "openPathOrFacingAction": "synthetic_open_path_or_facing_action",
        "openPathOrFacingCompletion": "synthetic_open_path_or_facing_completion",
        "patDrawState": "synthetic_pat_draw_state",
        "rawLeaf": "synthetic shape-only leaf; not source evidence",
        "remainingDraws": "synthetic_remaining_draws",
        "seat": "synthetic_seat",
        "seatModel": "synthetic_seat_model",
        "splitRule": "synthetic_split_pot_rule",
        "source": "synthetic_shape_only_no_exact_source_reference",
        "street": "3rd",
        "visibleCardModel": "synthetic_visible_card_model",
        "visibleDeadSnapshot": "synthetic_visible_dead_snapshot",
    }
    return values.get(key, f"synthetic_{slug}_{key}")


def synthetic_value_for_path(path: str, family_id: str, slug: str) -> Any:
    key = path.split(".")[-1]
    return synthetic_value_for_key(key, family_id, slug)


def ensure_non_empty_path(obj: dict[str, Any], path: str, family_id: str, slug: str) -> None:
    actual = get_path(obj, path)
    if not value_is_non_empty(actual) or is_template_placeholder(actual):
        set_path(obj, path, synthetic_value_for_path(path, family_id, slug))


def ensure_manifest_placeholder_path(obj: dict[str, Any], path: str) -> None:
    actual = get_path(obj, path)
    if not value_is_non_empty(actual):
        set_path(obj, path, "<required-synthetic-shape-only-no-real-lineage>")


def build_candidate_ranges(family_rule: dict[str, Any], family_id: str, slug: str) -> list[dict[str, Any]]:
    payload_markers = family_rule["minimumPayloadMarkers"]
    node: dict[str, Any] = {}
    for key in payload_markers["packRequiredNodeKeys"]:
        if key == "entries":
            continue
        node[key] = synthetic_value_for_key(key, family_id, slug)
    entry = {
        key: synthetic_value_for_key(key, family_id, slug)
        for key in payload_markers["packRequiredEntryKeys"]
    }
    entry["inclusionState"] = "synthetic_shape_only_non_grounding"
    entry["frequency"] = None
    node["entries"] = [entry]
    return [node]


def materialize_shape_only_pack(pack: dict[str, Any], family_rule: dict[str, Any], slug: str) -> dict[str, Any]:
    family_id = family_rule["familyId"]
    payload_markers = family_rule["minimumPayloadMarkers"]
    for rule in payload_markers["packRequiredLiteralPaths"]:
        set_path(pack, rule["path"], rule["expected"])
    for path in payload_markers["packRequiredNonEmptyPaths"]:
        ensure_non_empty_path(pack, path, family_id, slug)
    for path in ["meta.name", "meta.gameForm", "meta.source", "meta.license"]:
        ensure_non_empty_path(pack, path, family_id, slug)
    pack["templateStatus"] = SYNTHETIC_STATUS
    pack["currentRepoStatus"] = family_rule["currentRepoStatus"]
    pack["syntheticFixtureStatus"] = SYNTHETIC_STATUS
    pack["syntheticFixtureNotice"] = "Synthetic shape-only fixture. It is not source evidence and carries no exact source path or source hash."
    pack["nonGroundingReason"] = "Synthetic family-shaped regression fixture only. It intentionally lacks exact source lineage and must not ground or promote this family."
    pack.setdefault("meta", {})["notes"] = "Synthetic shape-only non-grounding fixture generated from repo-local template and registry rules. No real source has been found."
    pack["candidateRanges"] = build_candidate_ranges(family_rule, family_id, slug)
    return pack


def ensure_transformation_stages(manifest: dict[str, Any], required_stages: list[str]) -> None:
    provenance = manifest.setdefault("provenance", {})
    chain = provenance.get("transformationChain")
    if not isinstance(chain, list):
        chain = []
        provenance["transformationChain"] = chain
    existing = {
        stage.get("stage"): stage
        for stage in chain
        if isinstance(stage, dict) and isinstance(stage.get("stage"), str)
    }
    for stage_name in required_stages:
        if stage_name in existing:
            stage = existing[stage_name]
        else:
            stage = {"stage": stage_name}
            chain.append(stage)
        if stage_name == "retained_source_basis":
            stage.setdefault("path", "<required-synthetic-shape-only-no-real-retained-basis-path>")
            stage.setdefault("sha256OrEquivalentLinkage", "<required-synthetic-shape-only-no-real-retained-basis-linkage>")
        else:
            stage.setdefault("path", f"<required-synthetic-shape-only-no-real-{stage_name}-path>")
            stage.setdefault("sha256", f"<required-synthetic-shape-only-no-real-{stage_name}-sha256>")


def materialize_shape_only_manifest(manifest: dict[str, Any], family_rule: dict[str, Any], slug: str) -> dict[str, Any]:
    family_id = family_rule["familyId"]
    payload_markers = family_rule["minimumPayloadMarkers"]
    provenance_rules = family_rule["minimumRetainedProvenance"]
    for rule in payload_markers["manifestRequiredLiteralPaths"]:
        set_path(manifest, rule["path"], rule["expected"])
    for path in payload_markers["manifestRequiredNonEmptyPaths"]:
        ensure_non_empty_path(manifest, path, family_id, slug)
    for path in provenance_rules["requiredSourceFields"] + provenance_rules["requiredArtifactFields"] + provenance_rules["requiredProvenanceFields"]:
        ensure_manifest_placeholder_path(manifest, path)
    ensure_transformation_stages(manifest, provenance_rules["requiredTransformationStages"])
    manifest["templateStatus"] = SYNTHETIC_STATUS
    manifest["currentRepoStatus"] = family_rule["currentRepoStatus"]
    manifest["syntheticFixtureStatus"] = SYNTHETIC_STATUS
    manifest["syntheticFixtureNotice"] = "Synthetic shape-only fixture. It is not source evidence and carries no exact source path or source hash."
    manifest["nonGroundingReason"] = "Synthetic family-shaped regression fixture only. It intentionally keeps placeholder provenance and must not ground or promote this family."
    manifest.setdefault("notes", []).append("Synthetic shape-only non-grounding fixture generated from repo-local template and registry rules. No real source has been found.")
    return manifest


def build_metadata(
    *,
    candidate_id: str,
    family_id: str,
    slug: str,
    family_rule: dict[str, Any],
    expected_verdict: str,
    notes: str,
) -> dict[str, Any]:
    template_paths = family_rule["templatePaths"]
    return {
        "metadataVersion": "1.0",
        "candidateId": candidate_id,
        "familyId": family_id,
        "familySlug": slug,
        "candidateStatus": SYNTHETIC_STATUS,
        "currentRepoStatus": family_rule["currentRepoStatus"],
        "packFile": "pack.json",
        "manifestFile": "manifest.json",
        "expectedVerdict": expected_verdict,
        "notes": notes,
        "templateSources": {
            "packTemplatePath": template_paths["packTemplatePath"],
            "manifestTemplatePath": template_paths["manifestTemplatePath"],
        },
        "reservedPaths": {
            "sourceDir": "source",
            "intermediateDir": "intermediate",
        },
        "nonGroundingReason": "Synthetic shape-only fixture for regression coverage. It intentionally omits exact source lineage and cannot promote family status.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True, help="Blocked family id to materialize.")
    parser.add_argument("--candidate-id", required=True, help="Safe candidate id used as the candidate directory name.")
    parser.add_argument("--out-dir", required=True, help="Staging root directory.")
    parser.add_argument(
        "--registry",
        default=str(get_default_registry_path()),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    parser.add_argument(
        "--expected-verdict",
        default=DEFAULT_EXPECTED_VERDICT,
        help="Expected validator verdict for batch validation.",
    )
    parser.add_argument("--notes", default="Synthetic shape-only fixture; not source evidence.", help="Optional candidate notes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_repo_path(args.registry, repo_root)
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir

    registry, registry_error = load_registry(registry_path)
    if registry_error or registry is None:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [registry_error or "unknown_registry_error"]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    family_rule = find_family(registry, args.family)
    if family_rule is None:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [f"unknown family id: {args.family}"]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    id_error = validate_candidate_id(args.candidate_id)
    if id_error:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [id_error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    allowed_verdicts = set(registry.get("verdictVocabulary", {}))
    if args.expected_verdict and args.expected_verdict not in allowed_verdicts:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [f"unknown expected verdict: {args.expected_verdict}"]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    slug = family_slug(args.family)
    candidate_dir = out_dir / slug / args.candidate_id
    if candidate_dir.exists():
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [f"candidate directory already exists: {candidate_dir}"]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    template_paths = family_rule["templatePaths"]
    pack_template = resolve_repo_path(template_paths["packTemplatePath"], repo_root)
    manifest_template = resolve_repo_path(template_paths["manifestTemplatePath"], repo_root)
    missing_templates = [str(path) for path in [pack_template, manifest_template] if not path.is_file()]
    if missing_templates:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [f"template_not_found: {path}" for path in missing_templates]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    pack_template_data, pack_error = load_json_object(pack_template)
    manifest_template_data, manifest_error = load_json_object(manifest_template)
    if pack_error or manifest_error or pack_template_data is None or manifest_template_data is None:
        json.dump({"shapeFixtureVersion": SHAPE_FIXTURE_VERSION, "status": "error", "errors": [error for error in [pack_error, manifest_error] if error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    candidate_dir.mkdir(parents=True)
    source_dir = candidate_dir / "source"
    intermediate_dir = candidate_dir / "intermediate"
    source_dir.mkdir()
    intermediate_dir.mkdir()

    pack_path = candidate_dir / "pack.json"
    manifest_path = candidate_dir / "manifest.json"
    metadata_path = candidate_dir / "candidate.json"
    pack = materialize_shape_only_pack(pack_template_data, family_rule, slug)
    manifest = materialize_shape_only_manifest(manifest_template_data, family_rule, slug)
    metadata = build_metadata(
        candidate_id=args.candidate_id,
        family_id=args.family,
        slug=slug,
        family_rule=family_rule,
        expected_verdict=args.expected_verdict,
        notes=args.notes,
    )

    write_json(pack_path, pack)
    write_json(manifest_path, manifest)
    write_json(metadata_path, metadata)

    payload = {
        "shapeFixtureVersion": SHAPE_FIXTURE_VERSION,
        "status": "ok",
        "familyId": args.family,
        "familySlug": slug,
        "candidateId": args.candidate_id,
        "candidateDir": str(candidate_dir),
        "fixtureStatus": SYNTHETIC_STATUS,
        "expectedVerdict": args.expected_verdict,
        "filesWritten": [
            str(metadata_path),
            str(pack_path),
            str(manifest_path),
        ],
        "reservedDirs": [
            str(source_dir),
            str(intermediate_dir),
        ],
        "nonGroundingReason": "Synthetic shape-only fixture; no real source path, source hash, or provenance-complete evidence is provided.",
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
