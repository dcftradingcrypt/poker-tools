#!/usr/bin/env python3
"""Materialize the retained PreflopAdvisor HU-100bb-with-limp source into a family-shaped candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0"
DEFAULT_REGISTRY = "out/_codex/mix_game_family_contract_registry.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_arg: str, root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return root / path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def candidate_relative(path: Path, candidate_dir: Path) -> str:
    return path.resolve().relative_to(candidate_dir.resolve()).as_posix()


def parse_tree_info(raw: str) -> dict[str, str]:
    parts = [part.strip() for part in raw.split(",", 4)]
    if len(parts) != 5:
        raise ValueError(f"unexpected TreeInfos entry shape: {raw}")
    return {
        "plrs": parts[0],
        "bb": parts[1],
        "game": parts[2],
        "folder": parts[3],
        "infos": parts[4],
    }


def parse_config(zf: zipfile.ZipFile) -> tuple[ConfigParser, dict[str, str]]:
    config_path = next(name for name in zf.namelist() if name.endswith("preflop_advisor/config.ini"))
    parser = ConfigParser()
    parser.read_string(zf.read(config_path).decode("utf-8", "replace"))
    tree_info = parse_tree_info(parser["TreeInfos"]["Table12"])
    return parser, tree_info


def positions_for_tree(parser: ConfigParser, tree_info: dict[str, str]) -> list[str]:
    positions = [item.strip() for item in parser["TreeReader"]["Positions"].split(",") if item.strip()]
    num_players = int(tree_info["plrs"])
    return list(reversed(positions[:num_players]))


def code_to_action_map(parser: ConfigParser) -> dict[str, str]:
    mapping: dict[str, str] = {}
    canonical_names = {
        "fold": "Fold",
        "call": "Call",
        "raisepot": "RaisePot",
        "raise75": "Raise75",
        "raise100": "Raise100",
        "raise60": "Raise60",
        "raise70": "Raise70",
        "3xopen": "3xOpen",
        "all_in": "All_In",
    }
    for key, value in parser["TreeReader"].items():
        if key in {"ending", "positions", "raisesizelist", "validactions", "cachesize"}:
            continue
        action_name = canonical_names.get(key, key)
        mapping[value.strip()] = action_name
    return mapping


def prettify_action(action_name: str) -> str:
    return {
        "Fold": "Fold",
        "Call": "Call",
        "Raise75": "Raise75",
        "RaisePot": "RaisePot",
        "Raise100": "Raise100",
        "All_In": "AllIn",
        "3xOpen": "3xOpen",
        "fold": "Fold",
        "call": "Call",
        "raise75": "Raise75",
        "raisepot": "RaisePot",
        "raise100": "Raise100",
        "all_in": "AllIn",
    }.get(action_name, action_name)


def parse_action_sequence(filename: str, seats: list[str], code_map: dict[str, str]) -> list[dict[str, str]]:
    stem = filename[:-4] if filename.endswith(".rng") else filename
    tokens = [] if not stem else stem.split(".")
    sequence: list[dict[str, str]] = []
    for index, token in enumerate(tokens):
        sequence.append(
            {
                "seat": seats[index % len(seats)],
                "actionCode": token,
                "actionName": code_map.get(token, f"UNKNOWN_{token}"),
                "actionLabel": prettify_action(code_map.get(token, f"UNKNOWN_{token}")),
            }
        )
    return sequence


def prior_path_label(sequence: list[dict[str, str]]) -> str:
    prior = sequence[:-1]
    if not prior:
        return "root"
    return " > ".join(f"{item['seat']}:{item['actionLabel']}" for item in prior)


def read_rng_pairs(zf: zipfile.ZipFile, path: str) -> list[tuple[str, str]]:
    lines = zf.read(path).decode("utf-8", "replace").splitlines()
    return list(zip(lines[0::2], lines[1::2]))


def representative_entries(
    pairs: list[tuple[str, str]],
    *,
    file_name: str,
    file_sha: str,
    sample_size: int = 3,
) -> tuple[list[dict[str, Any]], int]:
    parsed: list[tuple[str, float, float, str]] = []
    non_zero = 0
    for hand_token, raw in pairs:
        parts = raw.split(";", 1)
        try:
            frequency = float(parts[0])
        except ValueError:
            frequency = 0.0
        try:
            ev = float(parts[1]) if len(parts) > 1 else 0.0
        except ValueError:
            ev = 0.0
        if frequency > 0:
            non_zero += 1
        parsed.append((hand_token, frequency, ev, raw))

    ranked = sorted(parsed, key=lambda item: (item[1], item[2], item[0]), reverse=True)
    chosen = ranked[:sample_size]
    if not chosen and parsed:
        chosen = parsed[:1]

    entries = [
        {
            "handToken": hand_token,
            "rawLeaf": {
                "sourceFile": file_name,
                "sourceFileSha": file_sha,
                "frequency": frequency,
                "evMilliSmallBlind": ev,
                "rawLine": raw,
            },
        }
        for hand_token, frequency, ev, raw in chosen
    ]
    return entries, non_zero


def build_nodes(
    *,
    zf: zipfile.ZipFile,
    listing: list[dict[str, Any]],
    seats: list[str],
    code_map: dict[str, str],
    effective_stack_label: str,
    betting_model: str,
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    sha_by_name = {item["name"]: item["sha"] for item in listing if isinstance(item, dict) and "name" in item and "sha" in item}
    paths_by_name = {item["name"]: item["path"] for item in listing if isinstance(item, dict) and "name" in item and "path" in item}
    sorted_listing = sorted(
        [item for item in listing if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].endswith(".rng")],
        key=lambda item: item["name"],
    )

    nodes: list[dict[str, Any]] = []
    open_path_values: set[str] = set()
    node_summary: list[dict[str, Any]] = []

    for item in sorted_listing:
        file_name = item["name"]
        file_path = next(path for path in zf.namelist() if path.endswith(item["path"]))
        sequence = parse_action_sequence(file_name, seats, code_map)
        if not sequence:
            continue
        pairs = read_rng_pairs(zf, file_path)
        entries, non_zero_count = representative_entries(
            pairs,
            file_name=file_name,
            file_sha=sha_by_name[file_name],
        )
        decision_context = prior_path_label(sequence)
        open_path_values.add(decision_context)
        nodes.append(
            {
                "decisionNodeId": file_name[:-4],
                "seat": sequence[-1]["seat"],
                "effectiveStackBandOrSpr": effective_stack_label,
                "bettingModel": betting_model,
                "openPathOrFacingAction": decision_context,
                "entries": entries,
                "sourceFile": file_name,
                "sourcePathInArchive": paths_by_name[file_name],
                "sourceFileSha": sha_by_name[file_name],
                "selectedAction": sequence[-1]["actionLabel"],
                "sourceActionSequence": sequence,
                "sourceEntryCount": len(pairs),
                "sourceNonZeroEntryCount": non_zero_count,
            }
        )
        node_summary.append(
            {
                "decisionNodeId": file_name[:-4],
                "seat": sequence[-1]["seat"],
                "selectedAction": sequence[-1]["actionLabel"],
                "openPathOrFacingAction": decision_context,
                "sourceEntryCount": len(pairs),
                "sourceNonZeroEntryCount": non_zero_count,
            }
        )

    materialization_summary = {
        "nodeCount": len(nodes),
        "sourceRngFileCount": len(sorted_listing),
        "sourceEntryCountPerNode": sorted({node["sourceEntryCount"] for node in nodes}),
        "selectorAxes": {
            "seat": sorted({node["seat"] for node in nodes}),
            "effectiveStackBandOrSpr": sorted({node["effectiveStackBandOrSpr"] for node in nodes}),
            "bettingModel": sorted({node["bettingModel"] for node in nodes}),
            "openPathOrFacingActionCount": len(open_path_values),
        },
        "nodeSummary": node_summary[:8],
    }
    return nodes, sorted(open_path_values), materialization_summary


def load_seeded_sources(candidate: dict[str, Any], candidate_dir: Path) -> dict[str, Any]:
    seeded = candidate.get("seededSourceSummary", {})
    if not isinstance(seeded, dict):
        raise ValueError("candidate.json missing seededSourceSummary")
    sources = seeded.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("candidate.json seededSourceSummary.sources missing_or_not_list")
    resolved: dict[str, Any] = {}
    for item in sources:
        if not isinstance(item, dict):
            continue
        retained_path = item.get("retainedPath")
        if not isinstance(retained_path, str):
            continue
        path = candidate_dir / retained_path
        if retained_path.endswith(".zip"):
            resolved["zip"] = {"path": path, "meta": item}
        elif retained_path.endswith("_contents.json"):
            resolved["listing"] = {"path": path, "meta": item}
        elif retained_path.endswith("README.org"):
            resolved["readme"] = {"path": path, "meta": item}
        elif retained_path.endswith("LICENSE"):
            resolved["license"] = {"path": path, "meta": item}
    if "zip" not in resolved or "listing" not in resolved:
        raise ValueError("candidate.json seededSourceSummary missing zip or contents listing")
    return resolved


def build_batch_spec(candidate_dir: Path, family_id: str, candidate_id: str, expected_verdict: str) -> dict[str, Any]:
    return {
        "batchSpecVersion": "1.0",
        "batchId": f"materialized-{candidate_id}",
        "description": "Candidate-specific materialization rerun for retained PreflopAdvisor cc_high / 4-card source.",
        "registryPath": "out/_codex/mix_game_family_contract_registry.json",
        "pathBase": "repo_root",
        "generatedBy": "scripts/materialize_cc_high_4card_preflopadvisor_candidate.py",
        "candidateEntrySchema": {
            "required": ["candidateId", "familyId", "packPath", "manifestPath"],
            "optional": ["notes", "expectedVerdict"],
        },
        "candidates": [
            {
                "candidateId": candidate_id,
                "familyId": family_id,
                "packPath": str(candidate_dir / "pack.json"),
                "manifestPath": str(candidate_dir / "manifest.json"),
                "expectedVerdict": expected_verdict,
                "notes": "Materialized from retained PreflopAdvisor exact-commit source bundle; still non-grounding until family status is explicitly reviewed.",
            }
        ],
    }


def run_intake(root: Path, batch_spec: dict[str, Any], registry_path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "scripts/run_mix_game_candidate_intake.py", "--batch-spec", "-", "--registry", str(registry_path)],
        cwd=root,
        input=json.dumps(batch_spec, indent=2, sort_keys=True) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"run_mix_game_candidate_intake.py exit={completed.returncode}: {completed.stderr.strip()}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"intake output json decode error: line={exc.lineno} col={exc.colno} msg={exc.msg}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("intake output root_not_object")
    return payload


def build_workflow_summary(
    *,
    intake_dossier: dict[str, Any],
    source_seed_result: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates = intake_dossier.get("candidates", [])
    target = candidates[0] if isinstance(candidates, list) and candidates else {}
    review_verdict = target.get("reviewVerdict")
    return {
        "status": intake_dossier.get("status"),
        "sourceSeedStatus": None if not isinstance(source_seed_result, dict) else source_seed_result.get("status"),
        "copiedSourceCount": 0 if not isinstance(source_seed_result, dict) else len(source_seed_result.get("copiedSources", [])),
        "targetValidatorVerdict": target.get("validatorVerdict"),
        "targetReviewVerdict": review_verdict,
        "targetStillNonPromotable": isinstance(review_verdict, str) and review_verdict.startswith(("non_promotable_", "family_shape_match_missing_grounding_evidence")),
        "currentRepoStatusPreserved": target.get("currentRepoStatus") == "blocked_no_source",
        "byValidatorVerdict": intake_dossier.get("summary", {}).get("byValidatorVerdict", {}),
        "byReviewVerdict": intake_dossier.get("summary", {}).get("byReviewVerdict", {}),
        "executionErrorCount": intake_dossier.get("summary", {}).get("executionErrorCount", 0),
        "falsePositiveRiskCount": intake_dossier.get("summary", {}).get("falsePositiveRiskCount", 0),
        "intakeExecutionErrorCount": intake_dossier.get("summary", {}).get("executionErrorCount", 0),
        "promotionCandidatePendingHumanReviewCount": intake_dossier.get("summary", {}).get("promotionCandidatePendingHumanReviewCount", 0),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-dir",
        default="out/_private/mix_game_candidate_staging/cc_high_4_card/preflopadvisor_hu100bb_with_limp",
        help="Candidate directory to materialize.",
    )
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY,
        help="Contract registry JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    candidate_dir = resolve_path(args.candidate_dir, root)
    registry_path = resolve_path(args.registry, root)

    candidate_path = candidate_dir / "candidate.json"
    pack_path = candidate_dir / "pack.json"
    manifest_path = candidate_dir / "manifest.json"
    dossier_path = candidate_dir / "source_drop_workflow_dossier.json"

    candidate = read_json(candidate_path)
    pack = read_json(pack_path)
    manifest = read_json(manifest_path)
    existing_dossier = read_json(dossier_path) if dossier_path.is_file() else {}

    seeded_sources = load_seeded_sources(candidate, candidate_dir)
    zip_path = seeded_sources["zip"]["path"]
    listing_path = seeded_sources["listing"]["path"]
    listing = read_json(listing_path)
    if not isinstance(listing, list):
        raise SystemExit("listing json root_not_list")

    with zipfile.ZipFile(zip_path) as zf:
        parser, tree_info = parse_config(zf)
        seats = positions_for_tree(parser, tree_info)
        code_map = code_to_action_map(parser)
        betting_model = "pot_limit_hu_with_limp_raise75_raisepot_raise100_all_in"
        effective_stack_label = f"{tree_info['bb']}bb"
        nodes, open_paths, materialization_summary = build_nodes(
            zf=zf,
            listing=listing,
            seats=seats,
            code_map=code_map,
            effective_stack_label=effective_stack_label,
            betting_model=betting_model,
        )

    source_reference = seeded_sources["zip"]["meta"]["sourceReference"]
    retrieved_at = seeded_sources["zip"]["meta"]["retrievedAt"]
    zip_rel = seeded_sources["zip"]["meta"]["retainedPath"]
    listing_rel = seeded_sources["listing"]["meta"]["retainedPath"]
    zip_sha = seeded_sources["zip"]["meta"]["sha256"]
    listing_sha = seeded_sources["listing"]["meta"]["sha256"]
    game_form = tree_info["game"]
    seat_model = "heads_up_sb_bb"
    materialized_template_status = "materialized_retained_source_non_grounding"
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pack.update(
        {
            "templateStatus": materialized_template_status,
            "familyId": "cc_high / 4-card",
            "currentRepoStatus": "blocked_no_source",
            "nonGroundingReason": "Materialized from the retained exact-commit PreflopAdvisor source bundle. This candidate is family-shaped but remains non-grounding until a separate family-status decision and any fuller normalization review are completed.",
            "meta": {
                "name": "PreflopAdvisor HU-100bb-with-limp retained-source candidate",
                "gameForm": game_form,
                "familyId": "cc_high / 4-card",
                "boardModel": "community",
                "potResolutionModel": "high_only_single_pot",
                "privateCardCount": 4,
                "bettingModel": betting_model,
                "seatModel": seat_model,
                "source": source_reference,
                "license": "MIT",
                "notes": "Materialized from a retained public GitHub commit archive plus a retained GitHub API range listing sidecar. Candidate remains blocked_no_source.",
            },
            "decisionModel": {
                "nativeDecisionUnit": "preflop_first_entry_or_defend",
                "decisionNodeIdField": "decisionNodeId",
                "openPathOrFacingActionField": "openPathOrFacingAction",
                "effectiveStackField": "effectiveStackBandOrSpr",
                "handTokenField": "handToken",
                "rawLeafField": "rawLeaf",
                "sourceNodePolicy": "source_native_endpoint_files_with_representative_entries",
            },
            "selectorAxes": {
                "seat": sorted({node["seat"] for node in nodes}),
                "effectiveStackBandOrSpr": [effective_stack_label],
                "bettingModel": [betting_model],
                "openPathOrFacingAction": open_paths,
            },
            "nodeSchema": {
                "schemaStatus": "source_native_endpoint_nodes_materialized",
                "containerType": "node_list_from_rng_files_with_representative_entries",
                "nodeKeys": [
                    "decisionNodeId",
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                    "entries",
                ],
                "entryKeys": [
                    "handToken",
                    "rawLeaf",
                ],
                "materializationPolicy": "Each .rng file becomes one source-backed node with representative entries only; exhaustive hand-class normalization remains future work.",
            },
            "candidateRanges": nodes,
            "normalizationNotes": [
                "This materialization keeps the source family-native and avoids any two-card pushfold schema reduction.",
                "decisionNodeId uses the exact source file stem so the candidate remains anchored to retained source files.",
                "entries are representative samples from each .rng file rather than a fully expanded downstream consumer format.",
            ],
            "sourceStructure": {
                "retainedArchivePath": zip_rel,
                "retainedArchiveSha256": zip_sha,
                "retainedListingPath": listing_rel,
                "retainedListingSha256": listing_sha,
                "positionsInTreeOrder": seats,
                "treeInfo": tree_info,
                "treeReaderCodeMap": code_map,
            },
            "materializationSummary": materialization_summary,
        }
    )

    pack_text = json.dumps(pack, indent=2, sort_keys=True) + "\n"
    normalized_pack_sha = sha256_bytes(pack_text.encode("utf-8"))
    pack_path.write_text(pack_text, encoding="utf-8")

    manifest.update(
        {
            "templateStatus": materialized_template_status,
            "familyId": "cc_high / 4-card",
            "currentRepoStatus": "blocked_no_source",
            "nonGroundingReason": "The candidate is now materialized from retained source basis, but it remains blocked_no_source pending explicit family-status review.",
            "generatedAtUtc": now_utc,
            "source": {
                "name": "PreflopAdvisor HU-100bb-with-limp demo PLO ranges",
                "exactSourcePathOrReference": source_reference,
                "retainedBasisPath": zip_rel,
                "retainedBasisType": "github_commit_archive_zip",
                "retrievedAt": retrieved_at,
                "license": "MIT",
                "redistribution": "Retained from a public GitHub repository commit archive with bundled LICENSE. Solver-output reuse and redistribution beyond retained repo-local review input remain user-review items.",
            },
            "familyIdentity": {
                "familyId": "cc_high / 4-card",
                "gameForm": game_form,
                "boardModel": "community",
                "potResolutionModel": "high_only_single_pot",
                "privateCardCount": 4,
                "bettingModel": betting_model,
                "seatModel": seat_model,
                "nativeDecisionUnit": "preflop_first_entry_or_defend",
            },
            "normalization": {
                "packTemplatePath": "out/_codex/cc_high_4card_pack_template.json",
                "transformedIntermediatePath": listing_rel,
                "selectorAxes": [
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                ],
                "nodeIdentityFields": [
                    "decisionNodeId",
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                ],
                "normalizationNotes": [
                    "The retained GitHub API contents listing is used as the only machine-readable source-structure sidecar in this pass.",
                    "The normalized pack preserves exact source file stems as provisional node identity while fuller source-to-decision-node normalization remains future work.",
                ],
            },
            "artifacts": {
                "normalizedPackPath": "pack.json",
                "normalizedManifestPath": "manifest.json",
                "derivedBundlePath": "none",
                "acceptanceReportPath": "out/_codex/cc_high_4card_preflopadvisor_candidate.md",
            },
            "provenance": {
                "sourceSha256OrEquivalentLinkage": f"sha256:{zip_sha}",
                "transformationChain": [
                    {
                        "stage": "retained_source_basis",
                        "path": zip_rel,
                        "sha256OrEquivalentLinkage": f"sha256:{zip_sha}",
                    },
                    {
                        "stage": "transformed_intermediate",
                        "path": listing_rel,
                        "sha256": listing_sha,
                    },
                    {
                        "stage": "normalized_pack",
                        "path": "pack.json",
                        "sha256": normalized_pack_sha,
                    },
                ],
                "artifactHashes": {
                    "retainedBasisSha256": zip_sha,
                    "transformedIntermediateSha256": listing_sha,
                    "normalizedPackSha256": normalized_pack_sha,
                },
                "seededRetainedSources": manifest.get("provenance", {}).get("seededRetainedSources", {}),
            },
            "notes": [
                "Materialized from retained exact-commit PreflopAdvisor source files for cc_high / 4-card candidate review.",
                "This candidate intentionally remains blocked_no_source and non-promoting in this pass.",
                "Representative sample entries are source-backed, but full exhaustive normalization of every source hand class remains future work.",
            ],
        }
    )
    write_json(manifest_path, manifest)

    candidate.update(
        {
            "candidateStatus": "family_shaped_retained_source_candidate_non_grounding",
            "currentRepoStatus": "blocked_no_source",
            "expectedVerdict": "shape_match_missing_grounding_evidence",
            "templateStatus": materialized_template_status,
            "nonGroundingReason": "Candidate materialized from retained source basis, but currentRepoStatus remains blocked_no_source pending explicit family-status review.",
            "notes": "Materialized from retained PreflopAdvisor exact-commit source bundle into a family-shaped cc_high / 4-card candidate; still non-grounding.",
            "materializationSummary": {
                "scriptVersion": SCRIPT_VERSION,
                "retainedSourceStructure": {
                    "archivePath": zip_rel,
                    "archiveSha256": zip_sha,
                    "listingPath": listing_rel,
                    "listingSha256": listing_sha,
                    "rngFileCount": materialization_summary["sourceRngFileCount"],
                },
                "selectorAxes": {
                    "seat": sorted({node["seat"] for node in nodes}),
                    "effectiveStackBandOrSpr": [effective_stack_label],
                    "bettingModel": [betting_model],
                    "openPathOrFacingActionCount": len(open_paths),
                },
                "normalizedPackSha256": normalized_pack_sha,
            },
        }
    )
    write_json(candidate_path, candidate)

    batch_spec = build_batch_spec(candidate_dir, candidate["familyId"], candidate["candidateId"], candidate["expectedVerdict"])
    intake_dossier = run_intake(root, batch_spec, registry_path)

    updated_dossier = dict(existing_dossier) if isinstance(existing_dossier, dict) else {}
    updated_dossier.update(
        {
            "status": intake_dossier.get("status", "failed"),
            "registryPath": str(registry_path),
            "candidateDir": str(candidate_dir),
            "familyId": candidate["familyId"],
            "candidateId": candidate["candidateId"],
            "generatedBatchSpec": batch_spec,
            "intakeDossier": intake_dossier,
            "executionErrors": intake_dossier.get("executionErrors", []),
            "warnings": intake_dossier.get("coverageLimits", []),
            "coverageLimits": intake_dossier.get("coverageLimits", []),
            "summary": build_workflow_summary(
                intake_dossier=intake_dossier,
                source_seed_result=updated_dossier.get("sourceSeedResult"),
            ),
            "materializationResult": {
                "scriptVersion": SCRIPT_VERSION,
                "status": "ok",
                "gameForm": game_form,
                "bettingModel": betting_model,
                "seatModel": seat_model,
                "effectiveStackBandOrSpr": effective_stack_label,
                "sourceRngFileCount": materialization_summary["sourceRngFileCount"],
                "nodeCount": materialization_summary["nodeCount"],
                "normalizedPackSha256": normalized_pack_sha,
            },
        }
    )
    write_json(dossier_path, updated_dossier)

    output = {
        "scriptVersion": SCRIPT_VERSION,
        "status": "ok",
        "candidateDir": str(candidate_dir),
        "candidatePath": str(candidate_path),
        "packPath": str(pack_path),
        "manifestPath": str(manifest_path),
        "dossierPath": str(dossier_path),
        "materializationSummary": materialization_summary,
        "intakeStatus": intake_dossier.get("status"),
        "validatorVerdict": intake_dossier.get("summary", {}).get("byValidatorVerdict", {}),
        "reviewVerdict": intake_dossier.get("summary", {}).get("byReviewVerdict", {}),
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
