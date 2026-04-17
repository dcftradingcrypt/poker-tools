#!/usr/bin/env python3
"""Materialize the retained O8 chart HTML into a family-shaped cc_hilo / 4-card candidate."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0"
DEFAULT_REGISTRY = "out/_codex/mix_game_family_contract_registry.json"

TAB_ORDER = ["a2", "a3", "a4", "a5", "23"]
TAB_LABELS = {
    "a2": "A-2",
    "a3": "A-3",
    "a4": "A-4",
    "a5": "A-5",
    "23": "2-3",
}
POSITION_ORDER = ["lj", "hj", "co", "bu"]
POSITION_LABELS = {
    "lj": "LJ",
    "hj": "HJ",
    "co": "CO",
    "bu": "BU",
}

GAME_FORM = "O8"
SEAT_MODEL = "six_max_open_positions_lj_hj_co_bu"
BETTING_MODEL = "first_entry_open_chart_unspecified_sizing"
EFFECTIVE_STACK_LABEL = "not_specified_in_source"
OPEN_PATH_LABEL = "first_entry_open"
SPLIT_RULE = "hi_lo_split_pot"
LOW_QUALIFIER_RULE = "eight_or_better"
MATERIALIZED_TEMPLATE_STATUS = "materialized_retained_source_grounding_evidence_candidate"

TITLE_RE = re.compile(r"<title>(.*?)</title>")
TAB_START_RE = re.compile(r'<div class="table-wrapper(?: active)?" id="tab-([^"]+)">')
HAND_TYPE_RE = re.compile(r'<div class="cell hand-type">(.*?)</div>')
POS_CELL_RE = re.compile(r'<div class="cell pos (?:(header-cell) )?(lj|hj|co|bu)">(.*?)</div>')
VALUE_RE = re.compile(r'<span class="value ([^"]+)">(.*?)</span>')
TAG_RE = re.compile(r"<[^>]+>")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_arg: str, root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return root / path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def clean_text(raw: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub("", raw)).split())


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
        key = None
        if retained_path.endswith("index.html"):
            key = "html"
        elif retained_path.endswith("commit.json"):
            key = "commit"
        elif retained_path.endswith("repo.json"):
            key = "repo"
        elif retained_path.endswith(".zip"):
            key = "zip"
        if key is not None:
            resolved[key] = {"path": path, "meta": item}

    missing = [name for name in ("html", "commit", "repo", "zip") if name not in resolved]
    if missing:
        raise ValueError(f"candidate.json seededSourceSummary missing required retained sources: {', '.join(missing)}")
    return resolved


def parse_source_html(text: str) -> dict[str, Any]:
    title_match = TITLE_RE.search(text)
    title = clean_text(title_match.group(1)) if title_match else "O8 Six-Max Opens"

    tabs: dict[str, Any] = {}
    current_tab: str | None = None
    current_row: dict[str, Any] | None = None
    current_row_kind: str | None = None

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        tab_match = TAB_START_RE.search(line)
        if tab_match:
            current_tab = tab_match.group(1)
            tabs[current_tab] = {
                "tabId": current_tab,
                "tabLabel": TAB_LABELS.get(current_tab, current_tab),
                "header": {},
                "rows": [],
            }
            continue

        if current_tab is None:
            continue

        if line == '<div class="row header">':
            current_row = {"cells": {}, "lineStart": lineno}
            current_row_kind = "header"
            continue

        if line == '<div class="row">':
            current_row = {"cells": {}, "lineStart": lineno}
            current_row_kind = "data"
            continue

        if current_row is None:
            continue

        hand_type_match = HAND_TYPE_RE.search(line)
        if hand_type_match:
            current_row["handType"] = clean_text(hand_type_match.group(1))
            current_row["handTypeLine"] = lineno
            continue

        pos_match = POS_CELL_RE.search(line)
        if pos_match:
            pos_key = pos_match.group(2)
            inner = pos_match.group(3)
            value_match = VALUE_RE.search(inner)
            if value_match:
                value_class = value_match.group(1)
                value_text = clean_text(value_match.group(2))
            else:
                value_class = "header"
                value_text = clean_text(inner)
            current_row["cells"][pos_key] = {
                "position": POSITION_LABELS[pos_key],
                "valueClass": value_class,
                "text": value_text,
                "sourceLine": lineno,
            }
            continue

        if line == "</div>":
            cells = current_row.get("cells", {})
            if current_row_kind == "header" and cells:
                tabs[current_tab]["header"] = cells
            elif current_row_kind == "data" and cells:
                hand_type = current_row.get("handType")
                if not isinstance(hand_type, str) or not hand_type:
                    raise ValueError(f"missing handType inside tab {current_tab} near line {lineno}")
                tabs[current_tab]["rows"].append(
                    {
                        "handType": hand_type,
                        "cells": cells,
                        "sourceLineRange": [current_row["lineStart"], lineno],
                    }
                )
            current_row = None
            current_row_kind = None

    missing_tabs = [tab_id for tab_id in TAB_ORDER if tab_id not in tabs]
    if missing_tabs:
        raise ValueError(f"missing expected tabs: {', '.join(missing_tabs)}")

    for tab_id in TAB_ORDER:
        header = tabs[tab_id].get("header", {})
        rows = tabs[tab_id].get("rows", [])
        if not header:
            raise ValueError(f"tab {tab_id} missing header row")
        if not rows:
            raise ValueError(f"tab {tab_id} missing data rows")
        missing_positions = [pos_key for pos_key in POSITION_ORDER if pos_key not in header]
        if missing_positions:
            raise ValueError(f"tab {tab_id} header missing positions: {', '.join(missing_positions)}")
        for row in rows:
            row_missing_positions = [pos_key for pos_key in POSITION_ORDER if pos_key not in row["cells"]]
            if row_missing_positions:
                raise ValueError(f"tab {tab_id} row {row['handType']} missing positions: {', '.join(row_missing_positions)}")

    return {
        "title": title,
        "tabs": tabs,
    }


def build_intermediate_payload(
    *,
    parsed: dict[str, Any],
    html_rel: str,
    html_sha: str,
) -> dict[str, Any]:
    tabs_payload = []
    value_class_counter: Counter[str] = Counter()

    for tab_id in TAB_ORDER:
        tab = parsed["tabs"][tab_id]
        rows_payload = []
        for row in tab["rows"]:
            cell_payload = {}
            for pos_key in POSITION_ORDER:
                cell = row["cells"][pos_key]
                value_class_counter.update([cell["valueClass"]])
                cell_payload[POSITION_LABELS[pos_key]] = {
                    "sourceValueClass": cell["valueClass"],
                    "sourceValueText": cell["text"],
                    "sourceLine": cell["sourceLine"],
                }
            rows_payload.append(
                {
                    "handType": row["handType"],
                    "sourceLineRange": row["sourceLineRange"],
                    "cells": cell_payload,
                }
            )

        tabs_payload.append(
            {
                "tabId": tab_id,
                "tabLabel": tab["tabLabel"],
                "sourceHeaderTexts": {
                    POSITION_LABELS[pos_key]: tab["header"][pos_key]["text"]
                    for pos_key in POSITION_ORDER
                },
                "rowCount": len(tab["rows"]),
                "rows": rows_payload,
            }
        )

    return {
        "scriptVersion": SCRIPT_VERSION,
        "sourceTitle": parsed["title"],
        "retainedSourcePath": html_rel,
        "retainedSourceSha256": html_sha,
        "normalizedSeatOrder": [POSITION_LABELS[pos_key] for pos_key in POSITION_ORDER],
        "tabOrder": [TAB_LABELS[tab_id] for tab_id in TAB_ORDER],
        "tabs": tabs_payload,
        "summary": {
            "tabCount": len(tabs_payload),
            "rowCountByTab": {item["tabLabel"]: item["rowCount"] for item in tabs_payload},
            "valueClassCounts": dict(sorted(value_class_counter.items())),
            "specialHeaderNormalization": [
                {
                    "tabLabel": "2-3",
                    "normalizedSeat": "LJ",
                    "sourceHeaderText": parsed["tabs"]["23"]["header"]["lj"]["text"],
                    "note": "The source uses UTG text in the 2-3 tab for the earliest opening seat while the HTML class, filter controls, and normalized seat model remain lj/LJ.",
                }
            ],
        },
    }


def build_candidate_ranges(parsed: dict[str, Any], html_rel: str, html_sha: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    value_class_counter: Counter[str] = Counter()
    row_count_by_tab: dict[str, int] = {}
    source_header_texts: dict[str, dict[str, str]] = {}

    for tab_id in TAB_ORDER:
        tab = parsed["tabs"][tab_id]
        tab_label = tab["tabLabel"]
        row_count_by_tab[tab_label] = len(tab["rows"])
        source_header_texts[tab_label] = {
            POSITION_LABELS[pos_key]: tab["header"][pos_key]["text"]
            for pos_key in POSITION_ORDER
        }
        for pos_key in POSITION_ORDER:
            position = POSITION_LABELS[pos_key]
            header_text = tab["header"][pos_key]["text"]
            entries = []
            for row in tab["rows"]:
                cell = row["cells"][pos_key]
                value_class_counter.update([cell["valueClass"]])
                entries.append(
                    {
                        "handToken": f"{tab_label} :: {row['handType']}",
                        "rawLeaf": {
                            "sourceTabId": tab_id,
                            "sourceTabLabel": tab_label,
                            "sourceHandType": row["handType"],
                            "sourcePosition": position,
                            "sourcePositionHeaderText": header_text,
                            "sourceValueClass": cell["valueClass"],
                            "sourceValueText": cell["text"],
                            "sourceHtmlPath": html_rel,
                            "sourceHtmlSha256": html_sha,
                            "sourceLineRange": row["sourceLineRange"],
                            "sourceValueLine": cell["sourceLine"],
                        },
                        "inclusionState": cell["valueClass"],
                    }
                )

            nodes.append(
                {
                    "decisionNodeId": f"{tab_id}_{position.lower()}",
                    "seat": position,
                    "effectiveStackBandOrSpr": EFFECTIVE_STACK_LABEL,
                    "bettingModel": BETTING_MODEL,
                    "openPathOrFacingAction": OPEN_PATH_LABEL,
                    "splitRule": SPLIT_RULE,
                    "lowQualifierRule": LOW_QUALIFIER_RULE,
                    "entries": entries,
                    "sourceTabId": tab_id,
                    "sourceTabLabel": tab_label,
                    "sourcePositionHeaderText": header_text,
                    "sourceRowCount": len(tab["rows"]),
                }
            )

    summary = {
        "nodeCount": len(nodes),
        "rowCountByTab": row_count_by_tab,
        "entryCountPerNode": sorted({len(node["entries"]) for node in nodes}),
        "selectorAxes": {
            "seat": [POSITION_LABELS[pos_key] for pos_key in POSITION_ORDER],
            "effectiveStackBandOrSpr": [EFFECTIVE_STACK_LABEL],
            "bettingModel": [BETTING_MODEL],
            "openPathOrFacingAction": [OPEN_PATH_LABEL],
            "splitRule": [SPLIT_RULE],
            "lowQualifierRule": [LOW_QUALIFIER_RULE],
        },
        "valueClassCounts": dict(sorted(value_class_counter.items())),
        "sourceHeaderTexts": source_header_texts,
    }
    return nodes, summary


def build_batch_spec(candidate_dir: Path, family_id: str, candidate_id: str, expected_verdict: str) -> dict[str, Any]:
    return {
        "batchSpecVersion": "1.0",
        "batchId": f"materialized-{candidate_id}",
        "description": "Candidate-specific materialization rerun for retained O8 chart cc_hilo / 4-card source.",
        "registryPath": "out/_codex/mix_game_family_contract_registry.json",
        "pathBase": "repo_root",
        "generatedBy": "scripts/materialize_cc_hilo_4card_o8charts_candidate.py",
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
                "notes": "Materialized from the retained O8 exact-commit HTML chart; candidate remains blocked_no_source until a separate source-evidence decision lane.",
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
        default="out/_private/mix_game_candidate_staging/cc_hilo_4_card/o8_charts_6max_opening_ranges",
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
    intermediate_dir = candidate_dir / "intermediate"
    intermediate_path = intermediate_dir / "index_rows.json"

    candidate = read_json(candidate_path)
    pack = read_json(pack_path)
    manifest = read_json(manifest_path)
    existing_dossier = read_json(dossier_path) if dossier_path.is_file() else {}

    seeded_sources = load_seeded_sources(candidate, candidate_dir)
    html_path = seeded_sources["html"]["path"]
    commit_path = seeded_sources["commit"]["path"]
    repo_meta_path = seeded_sources["repo"]["path"]
    zip_path = seeded_sources["zip"]["path"]

    html_text = html_path.read_text(encoding="utf-8")
    parsed = parse_source_html(html_text)

    html_rel = seeded_sources["html"]["meta"]["retainedPath"]
    commit_rel = seeded_sources["commit"]["meta"]["retainedPath"]
    repo_rel = seeded_sources["repo"]["meta"]["retainedPath"]
    zip_rel = seeded_sources["zip"]["meta"]["retainedPath"]
    html_sha = seeded_sources["html"]["meta"]["sha256"]
    commit_sha = seeded_sources["commit"]["meta"]["sha256"]
    repo_sha = seeded_sources["repo"]["meta"]["sha256"]
    zip_sha = seeded_sources["zip"]["meta"]["sha256"]
    source_reference = seeded_sources["html"]["meta"]["sourceReference"]
    retrieved_at = seeded_sources["html"]["meta"]["retrievedAt"]
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    intermediate_dir.mkdir(parents=True, exist_ok=True)
    intermediate_payload = build_intermediate_payload(parsed=parsed, html_rel=html_rel, html_sha=html_sha)
    intermediate_text = json.dumps(intermediate_payload, indent=2, sort_keys=True) + "\n"
    intermediate_sha = sha256_bytes(intermediate_text.encode("utf-8"))
    intermediate_path.write_text(intermediate_text, encoding="utf-8")
    intermediate_rel = "intermediate/index_rows.json"

    nodes, materialization_summary = build_candidate_ranges(parsed, html_rel, html_sha)

    repo_meta = read_json(repo_meta_path)
    commit_meta = read_json(commit_path)
    repo_description = repo_meta.get("description")
    commit_message = commit_meta.get("commit", {}).get("message")
    source_name = parsed["title"]
    if isinstance(repo_description, str) and repo_description.strip():
        source_name = repo_description.strip()

    pack.update(
        {
            "templateStatus": MATERIALIZED_TEMPLATE_STATUS,
            "familyId": "cc_hilo / 4-card",
            "currentRepoStatus": "blocked_no_source",
            "nonGroundingReason": "Materialized from the retained exact-commit O8 HTML chart with provenance-complete candidate artifacts. currentRepoStatus remains blocked_no_source until a separate human source-evidence review and explicit family-status decision are completed.",
            "meta": {
                "name": "O8 Six-Max Opens retained-source candidate",
                "gameForm": GAME_FORM,
                "familyId": "cc_hilo / 4-card",
                "boardModel": "community",
                "potResolutionModel": "hi_lo_split_pot",
                "privateCardCount": 4,
                "bettingModel": BETTING_MODEL,
                "seatModel": SEAT_MODEL,
                "splitRule": SPLIT_RULE,
                "lowQualifierRule": LOW_QUALIFIER_RULE,
                "source": source_reference,
                "license": "not_declared_in_retained_repo_metadata",
                "notes": "Materialized from a retained public GitHub HTML chart plus retained commit/repo sidecars. The source covers 6-max first-entry opening guidance only and does not specify stack depth or raise sizing.",
            },
            "decisionModel": {
                "nativeDecisionUnit": "preflop_first_entry_or_defend_hi_lo",
                "decisionNodeIdField": "decisionNodeId",
                "openPathOrFacingActionField": "openPathOrFacingAction",
                "effectiveStackField": "effectiveStackBandOrSpr",
                "splitRuleField": "splitRule",
                "lowQualifierRuleField": "lowQualifierRule",
                "handTokenField": "handToken",
                "rawLeafField": "rawLeaf",
                "sourceNodePolicy": "one_node_per_tab_and_open_position_from_retained_html_chart",
            },
            "selectorAxes": {
                "seat": [POSITION_LABELS[pos_key] for pos_key in POSITION_ORDER],
                "effectiveStackBandOrSpr": [EFFECTIVE_STACK_LABEL],
                "bettingModel": [BETTING_MODEL],
                "openPathOrFacingAction": [OPEN_PATH_LABEL],
                "splitRule": [SPLIT_RULE],
                "lowQualifierRule": [LOW_QUALIFIER_RULE],
            },
            "payloadMarkers": {
                "requiredFamilyMarkers": {
                    "familyId": "cc_hilo / 4-card",
                    "boardModel": "community",
                    "potResolutionModel": "hi_lo_split_pot",
                    "privateCardCount": 4,
                    "splitRule": SPLIT_RULE,
                    "lowQualifierRule": LOW_QUALIFIER_RULE,
                },
                "requiredNodeFields": [
                    "decisionNodeId",
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                    "splitRule",
                    "lowQualifierRule",
                    "entries",
                ],
                "requiredEntryFields": [
                    "handToken",
                    "rawLeaf",
                ],
                "forbiddenOrFamilyMismatchMarkers": [
                    "potResolutionModel=high_only_single_pot",
                    "secondaryPositionsByPosition",
                    "rangeMode=open_jam",
                    "rangeMode=call_vs_jam",
                    "twoCard169Domain",
                ],
            },
            "nodeSchema": {
                "schemaStatus": "source_native_chart_nodes_materialized",
                "containerType": "node_list_from_tab_and_position_cells",
                "nodeKeys": [
                    "decisionNodeId",
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                    "splitRule",
                    "lowQualifierRule",
                    "entries",
                ],
                "entryKeys": [
                    "handToken",
                    "rawLeaf",
                    "inclusionState",
                ],
                "materializationPolicy": "Each source tab and opening position becomes one node; entries preserve source-native ALL/NONE/specific chart text rather than collapsing into inferred combo expansions.",
            },
            "candidateRanges": nodes,
            "normalizationNotes": [
                "The retained HTML chart is an opening-only family-native source, so every node uses openPathOrFacingAction=first_entry_open.",
                "The source does not specify stack depth or raise sizing; effectiveStackBandOrSpr and bettingModel therefore stay explicit as source-not-specified labels rather than inferred values.",
                "The 2-3 tab displays UTG text in the header for the lj column; normalization preserves LJ as the seat key while keeping the exact source header text in sourcePositionHeaderText.",
            ],
            "sourceStructure": {
                "retainedHtmlPath": html_rel,
                "retainedHtmlSha256": html_sha,
                "retainedArchivePath": zip_rel,
                "retainedArchiveSha256": zip_sha,
                "retainedCommitPath": commit_rel,
                "retainedCommitSha256": commit_sha,
                "retainedRepoMetadataPath": repo_rel,
                "retainedRepoMetadataSha256": repo_sha,
                "sourceTitle": parsed["title"],
                "repoDescription": repo_description,
                "sourceCommitMessage": commit_message,
                "normalizedSeatHeaders": materialization_summary["sourceHeaderTexts"],
            },
            "materializationSummary": materialization_summary,
        }
    )

    pack_text = json.dumps(pack, indent=2, sort_keys=True) + "\n"
    normalized_pack_sha = sha256_bytes(pack_text.encode("utf-8"))
    pack_path.write_text(pack_text, encoding="utf-8")

    manifest.update(
        {
            "templateStatus": MATERIALIZED_TEMPLATE_STATUS,
            "familyId": "cc_hilo / 4-card",
            "currentRepoStatus": "blocked_no_source",
            "nonGroundingReason": "The candidate is now materialized from retained source basis with complete candidate provenance, but the family remains blocked_no_source until a separate explicit review accepts the source evidence.",
            "generatedAtUtc": now_utc,
            "source": {
                "name": source_name,
                "exactSourcePathOrReference": source_reference,
                "retainedBasisPath": html_rel,
                "retainedBasisType": "html_chart",
                "retrievedAt": retrieved_at,
                "license": "not_declared_in_retained_repo_metadata",
                "redistribution": "Retained from a public GitHub HTML chart. Repo metadata does not declare a license, so downstream redistribution beyond repo-local review input remains a user review item.",
            },
            "familyIdentity": {
                "familyId": "cc_hilo / 4-card",
                "gameForm": GAME_FORM,
                "boardModel": "community",
                "potResolutionModel": "hi_lo_split_pot",
                "privateCardCount": 4,
                "bettingModel": BETTING_MODEL,
                "seatModel": SEAT_MODEL,
                "splitRule": SPLIT_RULE,
                "lowQualifierRule": LOW_QUALIFIER_RULE,
                "nativeDecisionUnit": "preflop_first_entry_or_defend_hi_lo",
            },
            "normalization": {
                "packTemplatePath": "out/_codex/cc_hilo_4card_pack_template.json",
                "transformedIntermediatePath": intermediate_rel,
                "selectorAxes": [
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                    "splitRule",
                    "lowQualifierRule",
                ],
                "nodeIdentityFields": [
                    "decisionNodeId",
                    "seat",
                    "effectiveStackBandOrSpr",
                    "bettingModel",
                    "openPathOrFacingAction",
                    "splitRule",
                    "lowQualifierRule",
                ],
                "normalizationNotes": [
                    "The transformed intermediate records the retained HTML chart rows directly, without inferring unstated stack or raise-size metadata.",
                    "The normalized pack preserves source-native ALL/NONE/specific chart text as rawLeaf rather than expanding combo filters into invented exact hand lists.",
                    "LJ remains the normalized earliest opening seat even where the 2-3 tab header text displays UTG in the retained source HTML.",
                ],
            },
            "artifacts": {
                "normalizedPackPath": "pack.json",
                "normalizedManifestPath": "manifest.json",
                "derivedBundlePath": "none",
                "acceptanceReportPath": "out/_codex/cc_hilo_4card_candidate.md",
            },
            "provenance": {
                "sourceSha256OrEquivalentLinkage": f"sha256:{html_sha}",
                "transformationChain": [
                    {
                        "stage": "retained_source_basis",
                        "path": html_rel,
                        "sha256OrEquivalentLinkage": f"sha256:{html_sha}",
                    },
                    {
                        "stage": "transformed_intermediate",
                        "path": intermediate_rel,
                        "sha256": intermediate_sha,
                    },
                    {
                        "stage": "normalized_pack",
                        "path": "pack.json",
                        "sha256": normalized_pack_sha,
                    },
                ],
                "artifactHashes": {
                    "retainedBasisSha256": html_sha,
                    "transformedIntermediateSha256": intermediate_sha,
                    "normalizedPackSha256": normalized_pack_sha,
                },
                "seededRetainedSources": manifest.get("provenance", {}).get("seededRetainedSources", {}),
            },
            "notes": [
                "Materialized from the retained O8 exact-commit HTML chart into a family-shaped cc_hilo / 4-card candidate.",
                "This candidate covers first-entry opening nodes only; defend coverage is not present in the retained source.",
                "The retained zip, commit metadata, and repo metadata remain as provenance sidecars, while source/index.html is the retained source basis for the normalized artifact.",
            ],
        }
    )
    write_json(manifest_path, manifest)

    candidate.update(
        {
            "candidateStatus": "family_shaped_retained_source_candidate_with_grounding_evidence",
            "currentRepoStatus": "blocked_no_source",
            "expectedVerdict": "shape_match_with_grounding_evidence_candidate",
            "templateStatus": MATERIALIZED_TEMPLATE_STATUS,
            "nonGroundingReason": "Candidate materialized from retained source basis with candidate-level grounding evidence, but currentRepoStatus remains blocked_no_source pending separate human source-evidence review.",
            "notes": "Materialized from retained O8 exact-commit HTML chart into a family-shaped cc_hilo / 4-card candidate with provenance-complete pack/manifest linkage.",
            "materializationSummary": {
                "scriptVersion": SCRIPT_VERSION,
                "retainedSourceStructure": {
                    "htmlPath": html_rel,
                    "htmlSha256": html_sha,
                    "archivePath": zip_rel,
                    "archiveSha256": zip_sha,
                    "intermediatePath": intermediate_rel,
                    "intermediateSha256": intermediate_sha,
                },
                "selectorAxes": materialization_summary["selectorAxes"],
                "nodeCount": materialization_summary["nodeCount"],
                "entryCountPerNode": materialization_summary["entryCountPerNode"],
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
                "gameForm": GAME_FORM,
                "bettingModel": BETTING_MODEL,
                "seatModel": SEAT_MODEL,
                "effectiveStackBandOrSpr": EFFECTIVE_STACK_LABEL,
                "splitRule": SPLIT_RULE,
                "lowQualifierRule": LOW_QUALIFIER_RULE,
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
        "intermediatePath": str(intermediate_path),
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
