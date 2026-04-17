#!/usr/bin/env python3
"""Initialize a blocked-family candidate staging directory from repo-local templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from validate_mix_game_candidate_family import get_default_registry_path, load_json_object


SCAFFOLD_VERSION = "1.0"
DEFAULT_EXPECTED_VERDICT = "candidate_non_grounding_template_match"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True, help="Blocked family id to scaffold.")
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
        help="Optional expected verdict for later batch validation.",
    )
    parser.add_argument("--notes", default="", help="Optional candidate notes for batch output.")
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
        json.dump(
            {
                "scaffoldVersion": SCAFFOLD_VERSION,
                "status": "error",
                "errors": [registry_error or "unknown_registry_error"],
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    family = find_family(registry, args.family)
    if family is None:
        error = f"unknown family id: {args.family}"
        json.dump({"scaffoldVersion": SCAFFOLD_VERSION, "status": "error", "errors": [error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    id_error = validate_candidate_id(args.candidate_id)
    if id_error:
        json.dump({"scaffoldVersion": SCAFFOLD_VERSION, "status": "error", "errors": [id_error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    allowed_verdicts = set(registry.get("verdictVocabulary", {}))
    if args.expected_verdict and args.expected_verdict not in allowed_verdicts:
        error = f"unknown expected verdict: {args.expected_verdict}"
        json.dump({"scaffoldVersion": SCAFFOLD_VERSION, "status": "error", "errors": [error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    slug = family_slug(args.family)
    candidate_dir = out_dir / slug / args.candidate_id
    if candidate_dir.exists():
        error = f"candidate directory already exists: {candidate_dir}"
        json.dump({"scaffoldVersion": SCAFFOLD_VERSION, "status": "error", "errors": [error]}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    template_paths = family["templatePaths"]
    pack_template = resolve_repo_path(template_paths["packTemplatePath"], repo_root)
    manifest_template = resolve_repo_path(template_paths["manifestTemplatePath"], repo_root)
    missing_templates = [str(path) for path in [pack_template, manifest_template] if not path.is_file()]
    if missing_templates:
        errors = [f"template_not_found: {path}" for path in missing_templates]
        json.dump({"scaffoldVersion": SCAFFOLD_VERSION, "status": "error", "errors": errors}, sys.stdout, indent=2, sort_keys=True)
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
    shutil.copyfile(pack_template, pack_path)
    shutil.copyfile(manifest_template, manifest_path)

    metadata = {
        "metadataVersion": "1.0",
        "candidateId": args.candidate_id,
        "familyId": args.family,
        "familySlug": slug,
        "candidateStatus": "candidate_non_grounding_scaffold",
        "currentRepoStatus": family["currentRepoStatus"],
        "packFile": "pack.json",
        "manifestFile": "manifest.json",
        "expectedVerdict": args.expected_verdict,
        "notes": args.notes,
        "templateSources": {
            "packTemplatePath": template_paths["packTemplatePath"],
            "manifestTemplatePath": template_paths["manifestTemplatePath"],
        },
        "reservedPaths": {
            "sourceDir": "source",
            "intermediateDir": "intermediate",
        },
        "nonGroundingReason": "Scaffolded from non-grounding templates for future candidate intake. This is not source evidence.",
    }
    write_json(metadata_path, metadata)

    payload = {
        "scaffoldVersion": SCAFFOLD_VERSION,
        "status": "ok",
        "familyId": args.family,
        "familySlug": slug,
        "candidateId": args.candidate_id,
        "candidateDir": str(candidate_dir),
        "filesWritten": [
            str(metadata_path),
            str(pack_path),
            str(manifest_path),
        ],
        "reservedDirs": [
            str(source_dir),
            str(intermediate_dir),
        ],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
