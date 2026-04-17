#!/usr/bin/env python3
"""Build a validator-ready batch spec from blocked-family candidate staging folders."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_family import get_default_registry_path, load_json_object


BUILDER_VERSION = "1.0"
SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def family_slug(family_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", family_id.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def resolve_path(path_arg: str, repo_root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return repo_root / path


def to_batch_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_registry(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    registry, error = load_json_object(path)
    if error:
        return None, error
    if not isinstance(registry.get("families"), list):
        return None, "registry.families missing_or_not_list"
    return registry, None


def load_metadata(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    data, error = load_json_object(path)
    if error:
        return None, error
    return data, None


def validate_simple_filename(value: Any, field: str) -> str | None:
    if not isinstance(value, str) or not value:
        return f"{field} missing_or_not_nonempty_string"
    if Path(value).name != value:
        return f"{field} must be a file name inside the candidate directory: {value}"
    return None


def validate_metadata(
    metadata: dict[str, Any],
    metadata_path: Path,
    family_by_id: dict[str, dict[str, Any]],
    allowed_verdicts: set[str],
) -> list[str]:
    errors: list[str] = []
    candidate_dir = metadata_path.parent
    family_dir = candidate_dir.parent

    family_id = metadata.get("familyId")
    candidate_id = metadata.get("candidateId")
    if not isinstance(family_id, str) or not family_id.strip():
        errors.append(f"{metadata_path}: familyId missing_or_not_nonempty_string")
    elif family_id not in family_by_id:
        errors.append(f"{metadata_path}: unknown familyId: {family_id}")
    else:
        expected_slug = family_slug(family_id)
        if family_dir.name != expected_slug:
            errors.append(f"{metadata_path}: family directory {family_dir.name} does not match expected slug {expected_slug}")

    if not isinstance(candidate_id, str) or not candidate_id.strip():
        errors.append(f"{metadata_path}: candidateId missing_or_not_nonempty_string")
    elif not SAFE_SEGMENT_RE.fullmatch(candidate_id):
        errors.append(f"{metadata_path}: candidateId must match ^[A-Za-z0-9][A-Za-z0-9._-]*$")
    elif candidate_dir.name != candidate_id:
        errors.append(f"{metadata_path}: candidate directory {candidate_dir.name} does not match candidateId {candidate_id}")

    for field in ["packFile", "manifestFile"]:
        error = validate_simple_filename(metadata.get(field), field)
        if error:
            errors.append(f"{metadata_path}: {error}")

    expected = metadata.get("expectedVerdict")
    if "expectedVerdict" in metadata and expected is not None and not isinstance(expected, str):
        errors.append(f"{metadata_path}: expectedVerdict not_string_or_null")
    elif isinstance(expected, str) and expected and expected not in allowed_verdicts:
        errors.append(f"{metadata_path}: unknown expectedVerdict: {expected}")

    return errors


def discover_metadata_paths(staging_root: Path) -> list[Path]:
    if not staging_root.is_dir():
        return []
    paths: list[Path] = []
    for family_dir in sorted(path for path in staging_root.iterdir() if path.is_dir()):
        for candidate_dir in sorted(path for path in family_dir.iterdir() if path.is_dir()):
            paths.append(candidate_dir / "candidate.json")
    return paths


def build_error_payload(staging_root: Path, registry_path: Path, errors: list[str]) -> dict[str, Any]:
    return {
        "batchSpecBuilderVersion": BUILDER_VERSION,
        "status": "error",
        "stagingRoot": str(staging_root),
        "registryPath": str(registry_path),
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-root", required=True, help="Root containing <family-slug>/<candidate-id>/candidate.json.")
    parser.add_argument(
        "--registry",
        default=str(get_default_registry_path()),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    parser.add_argument("--batch-id", default=None, help="Optional batch id. Defaults to staged-candidates-from-<root-name>.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_path(args.registry, repo_root)
    staging_root = Path(args.staging_root)
    if not staging_root.is_absolute():
        staging_root = Path.cwd() / staging_root

    registry, registry_error = load_registry(registry_path)
    if registry_error or registry is None:
        payload = build_error_payload(staging_root, registry_path, [registry_error or "unknown_registry_error"])
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    family_by_id = {entry["familyId"]: entry for entry in registry["families"]}
    family_order = {entry["familyId"]: index for index, entry in enumerate(registry["families"])}
    allowed_verdicts = set(registry.get("verdictVocabulary", {}))
    metadata_paths = discover_metadata_paths(staging_root)
    if not metadata_paths:
        payload = build_error_payload(staging_root, registry_path, [f"no staged candidates found under {staging_root}"])
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    errors: list[str] = []
    entries: list[dict[str, Any]] = []
    seen_candidate_ids: set[str] = set()

    for metadata_path in metadata_paths:
        if not metadata_path.is_file():
            errors.append(f"missing metadata: {metadata_path}")
            continue
        metadata, metadata_error = load_metadata(metadata_path)
        if metadata_error or metadata is None:
            errors.append(metadata_error or f"metadata unreadable: {metadata_path}")
            continue
        metadata_errors = validate_metadata(metadata, metadata_path, family_by_id, allowed_verdicts)
        errors.extend(metadata_errors)
        if metadata_errors:
            continue

        candidate_id = metadata["candidateId"]
        if candidate_id in seen_candidate_ids:
            errors.append(f"duplicate candidateId in staging build: {candidate_id}")
            continue
        seen_candidate_ids.add(candidate_id)

        candidate_dir = metadata_path.parent
        pack_path = candidate_dir / metadata["packFile"]
        manifest_path = candidate_dir / metadata["manifestFile"]
        file_errors: list[str] = []
        if not pack_path.is_file():
            file_errors.append(f"missing pack file for {candidate_id}: {pack_path}")
        if not manifest_path.is_file():
            file_errors.append(f"missing manifest file for {candidate_id}: {manifest_path}")
        if file_errors:
            errors.extend(file_errors)
            continue

        entry = {
            "candidateId": candidate_id,
            "familyId": metadata["familyId"],
            "packPath": to_batch_path(pack_path, repo_root),
            "manifestPath": to_batch_path(manifest_path, repo_root),
        }
        expected = metadata.get("expectedVerdict")
        notes = metadata.get("notes")
        if isinstance(expected, str) and expected:
            entry["expectedVerdict"] = expected
        if isinstance(notes, str) and notes:
            entry["notes"] = notes
        entries.append(entry)

    if errors:
        payload = build_error_payload(staging_root, registry_path, errors)
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    entries.sort(key=lambda item: (family_order[item["familyId"]], item["candidateId"]))
    batch_spec = {
        "batchSpecVersion": "1.0",
        "batchId": args.batch_id or f"staged-candidates-from-{staging_root.name}",
        "description": "Generated from blocked-family candidate staging directories. Validator success is not a family-status promotion.",
        "registryPath": to_batch_path(registry_path, repo_root),
        "pathBase": "repo_root",
        "generatedFromStagingRoot": str(staging_root),
        "candidateEntrySchema": {
            "required": ["candidateId", "familyId", "packPath", "manifestPath"],
            "optional": ["notes", "expectedVerdict"],
        },
        "candidates": entries,
    }
    json.dump(batch_spec, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
