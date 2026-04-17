#!/usr/bin/env python3
"""Seed retained source files into an existing blocked-family candidate directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_family import get_default_registry_path, load_json_object


SOURCE_SEED_VERSION = "1.0"
SEED_STATUS = "retained_sources_seeded_non_grounding"
SAFE_DEST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]*$")


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_candidate_relative(path: Path, candidate_dir: Path) -> str:
    try:
        return path.resolve().relative_to(candidate_dir.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_registry(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    registry, error = load_json_object(path)
    if error:
        return None, [error]
    if not isinstance(registry.get("families"), list):
        return None, ["registry.families missing_or_not_list"]
    return registry, []


def find_family(registry: dict[str, Any], family_id: str) -> dict[str, Any] | None:
    return next((entry for entry in registry["families"] if isinstance(entry, dict) and entry.get("familyId") == family_id), None)


def load_json_file(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    payload, error = load_json_object(path)
    if error:
        return None, [f"{label}: {error}"]
    return payload, []


def validate_simple_filename(value: Any, field: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return f"{field} missing_or_not_nonempty_string"
    if Path(value).name != value:
        return f"{field} must be a file name inside the candidate directory: {value}"
    return None


def source_reference_for(index: int, references: list[str]) -> str | None:
    if not references:
        return None
    if len(references) == 1:
        return references[0]
    return references[index]


def validate_source_references(source_count: int, references: list[str]) -> list[str]:
    if references and len(references) not in {1, source_count}:
        return [
            "source-reference count must be either one shared value or match the number of --source-file values"
        ]
    return []


def validate_candidate_layout(
    *,
    candidate_dir: Path,
    registry: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None, Path | None, Path | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not candidate_dir.is_dir():
        return None, None, None, None, None, None, [f"candidate_dir_not_found: {candidate_dir}"], warnings

    metadata_path = candidate_dir / "candidate.json"
    if not metadata_path.is_file():
        return None, None, None, None, None, None, [f"missing candidate.json: {metadata_path}"], warnings

    metadata, metadata_errors = load_json_file(metadata_path, "candidate.json")
    errors.extend(metadata_errors)
    if metadata is None:
        return None, None, None, None, None, None, errors, warnings

    family_id = metadata.get("familyId")
    candidate_id = metadata.get("candidateId")
    if not isinstance(family_id, str) or not family_id:
        errors.append("candidate.json familyId missing_or_not_nonempty_string")
        family = None
    else:
        family = find_family(registry, family_id)
        if family is None:
            errors.append(f"candidate.json familyId not in registry: {family_id}")

    if isinstance(family_id, str) and family is not None:
        expected_slug = family_slug(family_id)
        if candidate_dir.parent.name != expected_slug:
            errors.append(
                f"candidate family directory mismatch: actual={candidate_dir.parent.name} expected={expected_slug}"
            )
        metadata_slug = metadata.get("familySlug")
        if isinstance(metadata_slug, str) and metadata_slug and metadata_slug != expected_slug:
            errors.append(f"candidate.json familySlug mismatch: actual={metadata_slug} expected={expected_slug}")

    if isinstance(candidate_id, str) and candidate_id and candidate_dir.name != candidate_id:
        errors.append(f"candidate directory mismatch: actual={candidate_dir.name} candidateId={candidate_id}")

    pack_file_error = validate_simple_filename(metadata.get("packFile"), "packFile")
    manifest_file_error = validate_simple_filename(metadata.get("manifestFile"), "manifestFile")
    for error in [pack_file_error, manifest_file_error]:
        if error:
            errors.append(error)

    pack_path = candidate_dir / metadata.get("packFile", "pack.json") if isinstance(metadata.get("packFile"), str) else None
    manifest_path = candidate_dir / metadata.get("manifestFile", "manifest.json") if isinstance(metadata.get("manifestFile"), str) else None
    if pack_path is None or not pack_path.is_file():
        errors.append(f"missing pack file: {pack_path}")
    if manifest_path is None or not manifest_path.is_file():
        errors.append(f"missing manifest file: {manifest_path}")

    if errors:
        return metadata, None, None, family, pack_path, manifest_path, errors, warnings

    assert pack_path is not None
    assert manifest_path is not None
    pack, pack_errors = load_json_file(pack_path, "pack.json")
    manifest, manifest_errors = load_json_file(manifest_path, "manifest.json")
    errors.extend(pack_errors)
    errors.extend(manifest_errors)
    if pack is None or manifest is None:
        return metadata, pack, manifest, family, pack_path, manifest_path, errors, warnings

    for label, payload in [("pack", pack), ("manifest", manifest)]:
        payload_family = payload.get("familyId")
        if payload_family is not None and payload_family != family_id:
            errors.append(f"{label}.familyId mismatch: actual={payload_family} candidate={family_id}")
        current_status = payload.get("currentRepoStatus")
        if current_status is not None and current_status != "blocked_no_source":
            errors.append(f"{label}.currentRepoStatus must remain blocked_no_source, actual={current_status}")

    return metadata, pack, manifest, family, pack_path, manifest_path, errors, warnings


def validate_source_files(source_files: list[str], repo_root: Path, source_dir: Path) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    paths = [resolve_path(path_arg, repo_root) for path_arg in source_files]
    dest_names: set[str] = set()
    for path in paths:
        if not path.is_file():
            errors.append(f"source_file_not_found_or_not_file: {path}")
            continue
        dest_name = path.name
        if not dest_name or not SAFE_DEST_RE.fullmatch(dest_name):
            errors.append(f"unsafe_source_destination_name: {dest_name}")
            continue
        if dest_name in dest_names:
            errors.append(f"duplicate destination source filename: {dest_name}")
        dest_names.add(dest_name)
        dest_path = source_dir / dest_name
        if dest_path.exists():
            errors.append(f"destination_source_file_already_exists: {dest_path}")
    return paths, errors


def copy_sources(
    *,
    source_paths: list[Path],
    source_dir: Path,
    candidate_dir: Path,
    source_references: list[str],
    retrieved_at: str | None,
) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for index, source_path in enumerate(source_paths):
        dest_path = source_dir / source_path.name
        shutil.copyfile(source_path, dest_path)
        copied.append(
            {
                "index": index,
                "originalPath": str(source_path),
                "retainedPath": to_candidate_relative(dest_path, candidate_dir),
                "sha256": sha256_file(dest_path),
                "sizeBytes": dest_path.stat().st_size,
                "sourceReference": source_reference_for(index, source_references),
                "retrievedAt": retrieved_at,
            }
        )
    return copied


def append_note(manifest: dict[str, Any], note: str, warnings: list[str]) -> str:
    notes = manifest.get("notes")
    if notes is None:
        manifest["notes"] = [note]
        return "notes"
    if isinstance(notes, list):
        notes.append(note)
        return "notes[]"
    warnings.append("manifest.notes was not a list; wrote provenance.seededRetainedSources.note instead")
    return "provenance.seededRetainedSources.note"


def append_non_grounding_reason(existing: Any, addition: str) -> str:
    if isinstance(existing, str) and existing.strip():
        if addition in existing:
            return existing
        return f"{existing} {addition}"
    return addition


def update_metadata(
    metadata: dict[str, Any],
    *,
    family: dict[str, Any],
    copied_sources: list[dict[str, Any]],
    notes: list[str],
) -> list[str]:
    fields = [
        "candidateStatus",
        "currentRepoStatus",
        "templateStatus",
        "nonGroundingReason",
        "seededSourceSummary",
    ]
    metadata["candidateStatus"] = SEED_STATUS
    metadata["currentRepoStatus"] = family["currentRepoStatus"]
    metadata["templateStatus"] = SEED_STATUS
    metadata["nonGroundingReason"] = append_non_grounding_reason(
        metadata.get("nonGroundingReason"),
        "Retained source files were copied and hashed for intake staging only; this does not ground or promote the family.",
    )
    metadata["seededSourceSummary"] = {
        "sourceSeedVersion": SOURCE_SEED_VERSION,
        "seedStatus": SEED_STATUS,
        "sourceCount": len(copied_sources),
        "sources": copied_sources,
        "notes": notes,
        "nonGroundingReason": "Seeded retained-source files are review inputs only and are not normalized family-shaped grounding evidence.",
    }
    return fields


def update_manifest(
    manifest: dict[str, Any],
    *,
    family: dict[str, Any],
    copied_sources: list[dict[str, Any]],
    notes: list[str],
    warnings: list[str],
) -> list[str]:
    fields = [
        "currentRepoStatus",
        "templateStatus",
        "nonGroundingReason",
        "provenance.seededRetainedSources",
    ]
    manifest["currentRepoStatus"] = family["currentRepoStatus"]
    if not isinstance(manifest.get("templateStatus"), str) or not manifest["templateStatus"]:
        manifest["templateStatus"] = SEED_STATUS
    manifest["nonGroundingReason"] = append_non_grounding_reason(
        manifest.get("nonGroundingReason"),
        "Retained source files were copied and hashed under provenance.seededRetainedSources only; exact source lineage and normalized artifact provenance remain unproven.",
    )
    provenance = manifest.setdefault("provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
        manifest["provenance"] = provenance
        warnings.append("manifest.provenance was not an object; replaced with seeded provenance object")
        fields.append("provenance")
    provenance["seededRetainedSources"] = {
        "sourceSeedVersion": SOURCE_SEED_VERSION,
        "seedStatus": SEED_STATUS,
        "sourceCount": len(copied_sources),
        "sources": copied_sources,
        "notes": notes,
        "nonGroundingReason": "This block records copied retained-source files only. It does not fill exactSourcePathOrReference, sourceSha256OrEquivalentLinkage, retainedBasisPath, or normalized artifact hashes.",
    }
    note_field = append_note(
        manifest,
        "Retained-source files were seeded under provenance.seededRetainedSources as non-grounding intake material only.",
        warnings,
    )
    fields.append(note_field)
    return fields


def build_error_payload(
    *,
    candidate_dir: Path | None,
    registry_path: Path,
    errors: list[str],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "sourceSeedVersion": SOURCE_SEED_VERSION,
        "status": "error",
        "candidateDir": None if candidate_dir is None else str(candidate_dir),
        "registryPath": str(registry_path),
        "familyId": None,
        "copiedSources": [],
        "manifestFieldsTouched": [],
        "metadataFieldsTouched": [],
        "warnings": warnings or [],
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", required=True, help="Existing staged candidate directory.")
    parser.add_argument("--source-file", action="append", required=True, help="Retained source file to copy. Repeat for multiple files.")
    parser.add_argument(
        "--registry",
        default=str(get_default_registry_path()),
        help="Contract registry JSON path. Defaults to out/_codex/mix_game_family_contract_registry.json.",
    )
    parser.add_argument(
        "--source-reference",
        action="append",
        default=[],
        help="Optional source reference. Provide one shared value or one per --source-file.",
    )
    parser.add_argument("--retrieved-at", default=None, help="Optional user-supplied retrieval timestamp.")
    parser.add_argument("--note", action="append", default=[], help="Optional note to record in metadata and manifest seed blocks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()
    registry_path = resolve_path(args.registry, repo_root)
    candidate_dir = Path(args.candidate_dir)
    if not candidate_dir.is_absolute():
        candidate_dir = Path.cwd() / candidate_dir

    registry, registry_errors = load_registry(registry_path)
    if registry_errors or registry is None:
        json.dump(
            build_error_payload(candidate_dir=candidate_dir, registry_path=registry_path, errors=registry_errors),
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    metadata, _pack, manifest, family, _pack_path, manifest_path, layout_errors, warnings = validate_candidate_layout(
        candidate_dir=candidate_dir,
        registry=registry,
    )
    if layout_errors or metadata is None or manifest is None or family is None or manifest_path is None:
        json.dump(
            build_error_payload(candidate_dir=candidate_dir, registry_path=registry_path, errors=layout_errors, warnings=warnings),
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    reference_errors = validate_source_references(len(args.source_file), args.source_reference)
    source_dir = candidate_dir / "source"
    source_dir.mkdir(exist_ok=True)
    source_paths, source_errors = validate_source_files(args.source_file, repo_root, source_dir)
    errors = reference_errors + source_errors
    if errors:
        json.dump(
            build_error_payload(
                candidate_dir=candidate_dir,
                registry_path=registry_path,
                errors=errors,
                warnings=warnings,
            ),
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    copied_sources = copy_sources(
        source_paths=source_paths,
        source_dir=source_dir,
        candidate_dir=candidate_dir,
        source_references=args.source_reference,
        retrieved_at=args.retrieved_at,
    )
    metadata_fields = update_metadata(metadata, family=family, copied_sources=copied_sources, notes=args.note)
    manifest_fields = update_manifest(
        manifest,
        family=family,
        copied_sources=copied_sources,
        notes=args.note,
        warnings=warnings,
    )

    metadata_path = candidate_dir / "candidate.json"
    write_json(metadata_path, metadata)
    write_json(manifest_path, manifest)

    payload = {
        "sourceSeedVersion": SOURCE_SEED_VERSION,
        "status": "ok",
        "candidateDir": str(candidate_dir),
        "candidateId": metadata.get("candidateId"),
        "familyId": metadata.get("familyId"),
        "registryPath": str(registry_path),
        "copiedSources": copied_sources,
        "manifestPath": str(manifest_path),
        "manifestFieldsTouched": sorted(set(manifest_fields)),
        "metadataPath": str(metadata_path),
        "metadataFieldsTouched": sorted(set(metadata_fields)),
        "nonGroundingStatus": {
            "candidateStatus": metadata.get("candidateStatus"),
            "currentRepoStatus": metadata.get("currentRepoStatus"),
            "metadataTemplateStatus": metadata.get("templateStatus"),
            "manifestTemplateStatus": manifest.get("templateStatus"),
            "nonGroundingReason": metadata.get("nonGroundingReason"),
        },
        "warnings": warnings,
        "errors": [],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
