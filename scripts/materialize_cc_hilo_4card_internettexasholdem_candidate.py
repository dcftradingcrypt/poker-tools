#!/usr/bin/env python3
"""Materialize a retained Internet Texas Holdem Omaha Hi-Lo article into a cc_hilo / 4-card candidate."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0"
TEMPLATE_VERSION = "0.1"
TEMPLATE_STATUS = "materialized_retained_source_grounding_evidence_candidate"
CANDIDATE_STATUS = "family_shaped_retained_source_candidate_with_grounding_evidence"

FAMILY_ID = "cc_hilo / 4-card"
FAMILY_SLUG = "cc_hilo_4_card"
CANDIDATE_ID = "internettexasholdem_omaha_hi_lo_starting_hand_strategy_look_fors"
SOURCE_REFERENCE = "https://www.internettexasholdem.com/omaha-hi-lo-starting-hand-strategy-look-fors/"
SOURCE_NAME = "Internet Texas Holdem Omaha Hi-Lo Starting Hand Strategy Look-Fors article"
GAME_FORM = "Omaha Hi-Lo"
BETTING_MODEL = "betting_structure_not_specified_in_source_article"
SEAT_MODEL = "full_ring_relative_position_article_context"
SPLIT_RULE = "hi_lo_split_pot"
LOW_QUALIFIER_RULE = "eight_or_better"
EFFECTIVE_STACK_BAND = "not_specified_in_source_article"
PRACTICAL_USE_MODEL = "actionable_article_heuristics"
LICENSE_LABEL = "not_declared_in_retained_html"
REDISTRIBUTION_NOTE = (
    "Retained from a public Internet Texas Holdem strategy article. The retained page HTML does not "
    "declare a reusable license, so downstream redistribution beyond repo-local review remains a user review item."
)
RETAINED_BASIS_TYPE = "html_strategy_article"
PACK_TEMPLATE_PATH = "out/_codex/cc_hilo_4card_pack_template.json"
MANIFEST_TEMPLATE_PATH = "out/_codex/cc_hilo_4card_manifest_template.json"
DEFAULT_SOURCE_HTML = "/tmp/internettexasholdem_omaha_hi_lo_starting_hand_strategy_look_fors.html"
DEFAULT_CANDIDATE_DIR = (
    "out/_private/mix_game_candidate_staging/cc_hilo_4_card/"
    "internettexasholdem_omaha_hi_lo_starting_hand_strategy_look_fors"
)
GROUNDING_NOTE = (
    "This candidate was added after cc_hilo / 4-card had already been accepted as a grounded family. "
    "It preserves an additional retained article-derived source rather than serving as the original promotion basis."
)

HEADING_RE = re.compile(r"^Look-for #\d+:\s*(.+?)\s*$")
REVIEW_STOP_MARKERS = {"Submit your review", "Create your own review"}

NODE_SPECS: list[dict[str, Any]] = [
    {
        "heading": "Key Card",
        "decisionNodeId": "key_card",
        "seat": "not_specified_in_source_article_context",
        "effectiveStackBandOrSpr": EFFECTIVE_STACK_BAND,
        "bettingModel": BETTING_MODEL,
        "openPathOrFacingAction": "preflop_general_starting_hand_filter",
        "splitRule": SPLIT_RULE,
        "lowQualifierRule": LOW_QUALIFIER_RULE,
        "practical_entries": [
            {
                "heuristicId": "prefer_ace_based_starts_as_default",
                "scenarioLabel": "Use ace-containing starts as the default beginner filter",
                "recommendedAction": "prefer_ace_based_starting_hands",
                "actionClass": "beginner_primary_entry_filter",
                "appliesWhen": [
                    "Selecting Omaha Hi-Lo starting hands without a strong read on table texture",
                    "Beginning players who need a simple preflop baseline",
                ],
                "adjustOrFoldWhen": [
                    "Treat non-ace starts as exceptions rather than defaults while learning the game",
                ],
                "rationale": "The source calls the ace the key scooping card and says beginners lose little by ignoring most non-ace starts.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
            },
            {
                "heuristicId": "non_ace_exceptions_require_coordination",
                "scenarioLabel": "Non-ace hands need unusually strong coordination to justify play",
                "recommendedAction": "play_non_ace_hands_only_when_coordination_is_exceptional",
                "actionClass": "advanced_exception_rule",
                "appliesWhen": [
                    "Considering unusual non-ace hands such as KK23 or KKJQ double-suited",
                ],
                "adjustOrFoldWhen": [
                    "Fold most non-ace hands when their scoop potential is unclear or difficult to realize",
                ],
                "rationale": "The source allows a narrow class of non-ace exceptions but frames them as harder hands for beginners to play well.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
            },
        ],
    },
    {
        "heading": "Low Possibilities",
        "decisionNodeId": "low_possibilities",
        "seat": "button_full_ring_and_multiway_context_discussed",
        "effectiveStackBandOrSpr": EFFECTIVE_STACK_BAND,
        "bettingModel": BETTING_MODEL,
        "openPathOrFacingAction": "preflop_low_draw_selection_with_action_ahead_discussed",
        "splitRule": SPLIT_RULE,
        "lowQualifierRule": LOW_QUALIFIER_RULE,
        "practical_entries": [
            {
                "heuristicId": "fold_dry_a2xx_when_action_is_heavy",
                "scenarioLabel": "Dry A2XX is not an automatic continue once the pot is already crowded",
                "recommendedAction": "fold_dry_a2xx_in_heavy_multiway_action",
                "actionClass": "multiway_overcall_fold_rule",
                "appliesWhen": [
                    "Button or late-position spot with an early raise, callers, and additional aggression already in front",
                    "Your hand is mainly A2XX with little extra low backup or high coordination",
                ],
                "adjustOrFoldWhen": [
                    "Expect more quartering and domination when several players enter and many aces are already represented",
                    "Do not treat nut-low potential alone as sufficient equity in a heavily contested pot",
                ],
                "rationale": "The source explicitly calls dry A2XX over-valued and gives a concrete multiway reraised example where folding is correct.",
                "sourceRefs": [
                    {"kind": "paragraph", "ordinal": 2},
                    {"kind": "paragraph", "ordinal": 3},
                    {"kind": "paragraph", "ordinal": 5},
                ],
            },
            {
                "heuristicId": "prefer_a23x_or_a24x_backup",
                "scenarioLabel": "Low hands improve when the backup card survives counterfeit pressure",
                "recommendedAction": "prefer_a23x_or_a24x_over_bare_a2xx",
                "actionClass": "counterfeit_protection_rule",
                "appliesWhen": [
                    "Comparing A23X or A24X against low-only hands with no backup card",
                ],
                "adjustOrFoldWhen": [
                    "Upgrade starts that retain a nut-low draw after one wheel card gets counterfeited",
                ],
                "rationale": "The source singles out A23X and A24X because they keep nut-low potential after common counterfeit runouts.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 6}],
            },
            {
                "heuristicId": "avoid_a6xx_to_a8xx_for_low_only",
                "scenarioLabel": "A6XX, A7XX, and A8XX are weak low-only starters",
                "recommendedAction": "fold_a6xx_a7xx_a8xx_when_their_main_value_is_low_only",
                "actionClass": "nut_low_ceiling_rule",
                "appliesWhen": [
                    "Preflop evaluation of hands centered on A6XX, A7XX, or A8XX low potential",
                ],
                "adjustOrFoldWhen": [
                    "Do not continue simply because the hand contains an ace and one more low card",
                ],
                "rationale": "The source calls these hands junk because they cannot make the nut low and run into better lows too often.",
                "sourceRefs": [
                    {"kind": "paragraph", "ordinal": 7},
                    {"kind": "paragraph", "ordinal": 8},
                ],
            },
            {
                "heuristicId": "downgrade_a5xx_and_a4xx_without_support",
                "scenarioLabel": "A5XX and A4XX need better backup than many players assume",
                "recommendedAction": "downgrade_a5xx_and_a4xx_without_extra_low_or_high_support",
                "actionClass": "marginal_low_only_filter",
                "appliesWhen": [
                    "The hand's low value rests mostly on A5XX or A4XX without 2, 3, or strong high backup",
                ],
                "adjustOrFoldWhen": [
                    "Avoid full-ring out-of-position continues when another player already entered the pot",
                    "Require other good low cards or real high potential before continuing",
                ],
                "rationale": "The source labels A5XX marginal and A4XX unplayable for low alone unless stronger backup is present.",
                "sourceRefs": [
                    {"kind": "paragraph", "ordinal": 9},
                    {"kind": "paragraph", "ordinal": 10},
                ],
            },
            {
                "heuristicId": "dry_a3xx_needs_careful_pressure_read",
                "scenarioLabel": "Dry A3XX is good but not automatic in well-attended pots",
                "recommendedAction": "avoid_auto_continuing_dry_a3xx_when_second_best_low_risk_is_high",
                "actionClass": "quartered_or_second_best_low_rule",
                "appliesWhen": [
                    "Preflop and early-postflop planning with A3XX in a well-attended pot",
                ],
                "adjustOrFoldWhen": [
                    "Downgrade the hand when heavy action suggests better lows or quartering risk",
                ],
                "rationale": "The source describes A3XX as a good but often overplayed hand that becomes dangerous in jacked-up multiway spots.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 11}],
            },
            {
                "heuristicId": "low_draw_checklist_before_committing",
                "scenarioLabel": "Expect the downside with low draws unless the draw is premium and protected",
                "recommendedAction": "treat_low_draws_with_counterfeit_no_low_and_quartering_checks_before_committing",
                "actionClass": "pre_commit_checklist",
                "appliesWhen": [
                    "Evaluating whether to put substantial money in with a low draw",
                ],
                "adjustOrFoldWhen": [
                    "Check counterfeit risk on later streets",
                    "Check the chance that no qualifying low arrives",
                    "Check the chance of being quartered by another nut-low draw",
                    "Avoid early pot-jamming without premium backup and counterfeit protection",
                ],
                "rationale": "The source ends the section with explicit counterfeit, no-low, and quartering failure modes plus a warning against autopiloting low draws.",
                "sourceRefs": [
                    {"kind": "paragraph", "ordinal": 12},
                    {"kind": "bullet", "ordinal": 1},
                    {"kind": "bullet", "ordinal": 2},
                    {"kind": "bullet", "ordinal": 3},
                ],
            },
        ],
    },
    {
        "heading": "High Possibilities",
        "decisionNodeId": "high_possibilities",
        "seat": "late_position_heads_up_or_short_handed_context_discussed",
        "effectiveStackBandOrSpr": EFFECTIVE_STACK_BAND,
        "bettingModel": BETTING_MODEL,
        "openPathOrFacingAction": "preflop_high_only_selection_and_late_position_exception_discussed",
        "splitRule": SPLIT_RULE,
        "lowQualifierRule": LOW_QUALIFIER_RULE,
        "practical_entries": [
            {
                "heuristicId": "prefer_coordinated_double_suited_high_hands",
                "scenarioLabel": "High-only candidates need powerful coordinated two-card combinations",
                "recommendedAction": "prefer_double_suited_ace_king_or_wrap_style_high_hands",
                "actionClass": "coordinated_high_hand_preference",
                "appliesWhen": [
                    "Choosing among high-leaning Omaha Hi-Lo starting hands",
                ],
                "adjustOrFoldWhen": [
                    "Downgrade hands that lose too much when even one card is badly uncoordinated",
                ],
                "rationale": "The source highlights double-suited aces with kings and wrap-style holdings while stressing coordination as the key high-side ingredient.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 1}],
            },
            {
                "heuristicId": "value_high_hands_by_scoop_risk",
                "scenarioLabel": "A high hand improves when the board can block low entirely",
                "recommendedAction": "evaluate_high_hands_through_scoop_probability_not_just_raw_high_equity",
                "actionClass": "scoop_probability_filter",
                "appliesWhen": [
                    "Comparing high-only prospects on boards that may or may not allow a qualifying low",
                ],
                "adjustOrFoldWhen": [
                    "Upgrade high hands when board texture can prevent any low from existing",
                ],
                "rationale": "The source explains that some boards remove the low half entirely, which turns a good high hand into a scooping hand.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 2}],
            },
            {
                "heuristicId": "fold_mediocre_high_only_when_low_is_likely",
                "scenarioLabel": "High draws that mostly chase half the pot should be released when low completion is likely",
                "recommendedAction": "fold_mediocre_high_only_hands_when_low_probability_is_high",
                "actionClass": "half_pot_draw_fold_rule",
                "appliesWhen": [
                    "Late-position coordinated high hand enters multiway and sees a flop rich in low-making cards",
                ],
                "adjustOrFoldWhen": [
                    "Assume a split pot is likely when many low cards remain available",
                    "Do not chase second- or third-best high while drawing mostly to half the pot",
                ],
                "rationale": "The source walks through a multiway QJT-K style hand and concludes it should fold once the board strongly favors low realization.",
                "sourceRefs": [
                    {"kind": "paragraph", "ordinal": 3},
                    {"kind": "paragraph", "ordinal": 9},
                ],
            },
            {
                "heuristicId": "avoid_big_preflop_investment_with_high_only_multiway",
                "scenarioLabel": "High-only hands should not build large preflop pots by default",
                "recommendedAction": "keep_high_only_hands_cheap_unless_table_shape_is_favorable",
                "actionClass": "preflop_cost_control_rule",
                "appliesWhen": [
                    "Considering whether to put significant preflop money in with a hand that primarily wins high only",
                ],
                "adjustOrFoldWhen": [
                    "Prefer heads-up, short-handed, or favorable late-position steal conditions for aggressive exceptions",
                    "Fold more often when a normal multiway flop will favor low draws",
                ],
                "rationale": "The source says most flops lean low, so high-only hands should usually stay cheap unless the table is short-handed or steal-friendly.",
                "sourceRefs": [{"kind": "paragraph", "ordinal": 10}],
            },
        ],
    },
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_arg: str, root: Path) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return root / path


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(raw: str) -> str:
    text = html.unescape(raw.replace("\xa0", " "))
    text = text.replace("\u2019", "'")
    return " ".join(text.split())


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


class EntryContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_article = False
        self.in_entry_content = False
        self.entry_content_div_depth = 0
        self.capture_tag: str | None = None
        self.capture_text: list[str] = []
        self.article_title: str | None = None
        self.blocks: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key: value or "" for key, value in attrs}
        classes = attrs_map.get("class", "")
        if tag == "article":
            self.in_article = True

        if self.in_article and tag == "h1" and "entry-title" in classes:
            self.capture_tag = "h1"
            self.capture_text = []
            return

        if self.in_article and tag == "div" and "entry-content" in classes and not self.in_entry_content:
            self.in_entry_content = True
            self.entry_content_div_depth = 1
        elif self.in_entry_content and tag == "div":
            self.entry_content_div_depth += 1

        if self.in_entry_content and tag in {"p", "li"}:
            self.capture_tag = tag
            self.capture_text = []

    def handle_endtag(self, tag: str) -> None:
        if self.capture_tag == tag:
            text = clean_text(" ".join(self.capture_text))
            if text:
                if tag == "h1":
                    self.article_title = text
                else:
                    kind = "paragraph" if tag == "p" else "bullet"
                    self.blocks.append({"kind": kind, "text": text})
            self.capture_tag = None
            self.capture_text = []

        if self.in_entry_content and tag == "div":
            self.entry_content_div_depth -= 1
            if self.entry_content_div_depth == 0:
                self.in_entry_content = False

        if tag == "article":
            self.in_article = False

    def handle_data(self, data: str) -> None:
        if self.capture_tag is not None:
            self.capture_text.append(data)


def parse_article_sections(html_text: str) -> dict[str, Any]:
    parser = EntryContentParser()
    parser.feed(html_text)
    sections: list[dict[str, Any]] = []
    lead_blocks: list[dict[str, str]] = []
    current_section: dict[str, Any] | None = None
    counts: dict[str, dict[str, int]] = {}

    for block in parser.blocks:
        if block["text"] in REVIEW_STOP_MARKERS:
            break
        heading_match = HEADING_RE.fullmatch(block["text"]) if block["kind"] == "paragraph" else None
        if heading_match:
            heading = clean_text(heading_match.group(1))
            current_section = {
                "heading": heading,
                "headingSlug": slugify(heading),
                "items": [],
            }
            sections.append(current_section)
            counts[heading] = {"paragraph": 0, "bullet": 0}
            continue

        if current_section is None:
            lead_blocks.append(block)
            continue

        counts[current_section["heading"]][block["kind"]] += 1
        current_section["items"].append(
            {
                "kind": block["kind"],
                "ordinal": counts[current_section["heading"]][block["kind"]],
                "text": block["text"],
            }
        )

    if not sections:
        raise ValueError("no look-for sections parsed from retained HTML")

    return {
        "articleTitle": parser.article_title or SOURCE_NAME,
        "leadBlocks": lead_blocks,
        "sections": sections,
    }


def find_section(parsed: dict[str, Any], heading: str) -> dict[str, Any]:
    for section in parsed["sections"]:
        if section["heading"] == heading:
            return section
    raise ValueError(f"required section missing: {heading}")


def index_section_items(section: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {(item["kind"], item["ordinal"]): item for item in section["items"]}


def resolve_source_items(section: dict[str, Any], refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index = index_section_items(section)
    resolved: list[dict[str, Any]] = []
    for ref in refs:
        key = (ref["kind"], ref["ordinal"])
        if key not in index:
            raise ValueError(
                f"missing source item for heading={section['heading']} kind={ref['kind']} ordinal={ref['ordinal']}"
            )
        item = index[key]
        resolved.append({"kind": item["kind"], "ordinal": item["ordinal"], "text": item["text"]})
    return resolved


def build_intermediate_payload(*, parsed: dict[str, Any], html_rel: str, html_sha: str) -> dict[str, Any]:
    selected_sections: list[dict[str, Any]] = []
    selected_headings = {spec["heading"] for spec in NODE_SPECS}
    for node_spec in NODE_SPECS:
        section = find_section(parsed, node_spec["heading"])
        item_payload = [
            {
                "entryId": f"{section['headingSlug']}::{item['kind']}_{item['ordinal']:02d}",
                "kind": item["kind"],
                "ordinal": item["ordinal"],
                "text": item["text"],
            }
            for item in section["items"]
        ]
        heuristics_payload = [
            {
                "heuristicId": heuristic["heuristicId"],
                "scenarioLabel": heuristic["scenarioLabel"],
                "recommendedAction": heuristic["recommendedAction"],
                "actionClass": heuristic["actionClass"],
                "appliesWhen": list(heuristic.get("appliesWhen", [])),
                "adjustOrFoldWhen": list(heuristic.get("adjustOrFoldWhen", [])),
                "rationale": heuristic["rationale"],
                "sourceItems": resolve_source_items(section, heuristic["sourceRefs"]),
            }
            for heuristic in node_spec["practical_entries"]
        ]
        selected_sections.append(
            {
                "decisionNodeId": node_spec["decisionNodeId"],
                "heading": section["heading"],
                "headingSlug": section["headingSlug"],
                "itemCount": len(item_payload),
                "items": item_payload,
                "practicalHeuristicCount": len(heuristics_payload),
                "practicalHeuristics": heuristics_payload,
            }
        )

    unused_sections = [
        {
            "heading": section["heading"],
            "headingSlug": section["headingSlug"],
            "itemCount": len(section["items"]),
        }
        for section in parsed["sections"]
        if section["heading"] not in selected_headings
    ]

    return {
        "materializer": "internettexasholdem_omaha_hi_lo_article_sections",
        "scriptVersion": SCRIPT_VERSION,
        "familyId": FAMILY_ID,
        "articleTitle": parsed["articleTitle"],
        "sourceHtmlPath": html_rel,
        "sourceHtmlSha256": html_sha,
        "leadBlocks": parsed["leadBlocks"],
        "selectedSections": selected_sections,
        "unusedSections": unused_sections,
    }


def build_candidate_ranges(
    *,
    parsed: dict[str, Any],
    html_rel: str,
    html_sha: str,
    intermediate_rel: str,
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for node_spec in NODE_SPECS:
        section = find_section(parsed, node_spec["heading"])
        entries = []
        for heuristic in node_spec["practical_entries"]:
            source_items = resolve_source_items(section, heuristic["sourceRefs"])
            entries.append(
                {
                    "handToken": f"{section['headingSlug']}::heuristic::{heuristic['heuristicId']}",
                    "inclusionState": "actionable_article_heuristic",
                    "frequency": None,
                    "practicalUseForm": PRACTICAL_USE_MODEL,
                    "heuristicId": heuristic["heuristicId"],
                    "scenarioLabel": heuristic["scenarioLabel"],
                    "recommendedAction": heuristic["recommendedAction"],
                    "actionClass": heuristic["actionClass"],
                    "appliesWhen": list(heuristic.get("appliesWhen", [])),
                    "adjustOrFoldWhen": list(heuristic.get("adjustOrFoldWhen", [])),
                    "rationale": heuristic["rationale"],
                    "rawLeaf": {
                        "sourceHeading": section["heading"],
                        "sourceHeadingSlug": section["headingSlug"],
                        "sourceHtmlPath": html_rel,
                        "sourceHtmlSha256": html_sha,
                        "sourceIntermediatePath": intermediate_rel,
                        "sourceItemKind": "heuristic_bundle",
                        "sourceRefs": source_items,
                        "sourceText": " ".join(item["text"] for item in source_items),
                        "sourceTexts": [item["text"] for item in source_items],
                    },
                }
            )
        node = {
            key: value
            for key, value in node_spec.items()
            if key not in {"heading", "practical_entries"}
        }
        node["entries"] = entries
        nodes.append(node)
    return nodes


def selector_axes_from_nodes(nodes: list[dict[str, Any]]) -> dict[str, list[Any]]:
    axes: dict[str, list[Any]] = {
        "seat": [],
        "effectiveStackBandOrSpr": [],
        "bettingModel": [],
        "openPathOrFacingAction": [],
        "splitRule": [],
        "lowQualifierRule": [],
    }
    for node in nodes:
        for axis in axes:
            value = node.get(axis)
            if value not in axes[axis]:
                axes[axis].append(value)
    return axes


def build_pack(
    *,
    candidate_ranges: list[dict[str, Any]],
    source_reference: str,
) -> dict[str, Any]:
    return {
        "templateStatus": TEMPLATE_STATUS,
        "templateVersion": TEMPLATE_VERSION,
        "familyId": FAMILY_ID,
        "currentRepoStatus": "grounded",
        "groundingDecisionNote": GROUNDING_NOTE,
        "meta": {
            "name": "cc_hilo / 4-card candidate from retained Internet Texas Holdem article",
            "gameForm": GAME_FORM,
            "familyId": FAMILY_ID,
            "boardModel": "community",
            "potResolutionModel": "hi_lo_split_pot",
            "privateCardCount": 4,
            "bettingModel": BETTING_MODEL,
            "seatModel": SEAT_MODEL,
            "splitRule": SPLIT_RULE,
            "lowQualifierRule": LOW_QUALIFIER_RULE,
            "practicalUseModel": PRACTICAL_USE_MODEL,
            "source": source_reference,
            "license": LICENSE_LABEL,
            "notes": (
                "Materialized from retained strategy-article evidence into family-native preflop heuristic "
                "nodes without inventing unsupported exact range charts."
            ),
        },
        "decisionModel": {
            "nativeDecisionUnit": "preflop_first_entry_or_defend_hi_lo",
            "decisionNodeIdField": "decisionNodeId",
            "seatField": "seat",
            "effectiveStackField": "effectiveStackBandOrSpr",
            "bettingModelField": "bettingModel",
            "openPathOrFacingActionField": "openPathOrFacingAction",
            "splitRuleField": "splitRule",
            "lowQualifierRuleField": "lowQualifierRule",
            "handTokenField": "handToken",
            "rawLeafField": "rawLeaf",
        },
        "selectorAxes": selector_axes_from_nodes(candidate_ranges),
        "candidateRanges": candidate_ranges,
        "normalizationNotes": [
            "The normalized candidate converts retained Omaha Hi-Lo article prose into actionable preflop heuristics instead of inventing seat-by-seat exact frequency charts.",
            "Each heuristic preserves exact paragraph and bullet references so article-derived guidance remains auditable against the retained HTML basis.",
            "Selector values the article does not specify remain explicitly labeled as source-unspecified rather than being backfilled from outside assumptions.",
        ],
        "excludedInheritedAssumptions": [
            "169-cell two-card hand domain",
            "stacksBb-first pushfold grid",
            "open_jam and call_vs_jam role labels",
            "jam_position and caller_position selector roles",
            "high_only_single_pot framing",
        ],
    }


def build_manifest(
    *,
    html_rel: str,
    html_sha: str,
    retrieved_at: str,
    intermediate_rel: str,
    intermediate_sha: str,
    pack_sha: str,
) -> dict[str, Any]:
    return {
        "templateStatus": TEMPLATE_STATUS,
        "templateVersion": TEMPLATE_VERSION,
        "familyId": FAMILY_ID,
        "currentRepoStatus": "grounded",
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "manifestVersion": "candidate-0.1",
        "groundingDecisionNote": GROUNDING_NOTE,
        "source": {
            "name": SOURCE_NAME,
            "exactSourcePathOrReference": SOURCE_REFERENCE,
            "retainedBasisPath": html_rel,
            "retainedBasisType": RETAINED_BASIS_TYPE,
            "retrievedAt": retrieved_at,
            "license": LICENSE_LABEL,
            "redistribution": REDISTRIBUTION_NOTE,
        },
        "familyIdentity": {
            "familyId": FAMILY_ID,
            "gameForm": GAME_FORM,
            "boardModel": "community",
            "potResolutionModel": "hi_lo_split_pot",
            "privateCardCount": 4,
            "bettingModel": BETTING_MODEL,
            "seatModel": SEAT_MODEL,
            "splitRule": SPLIT_RULE,
            "lowQualifierRule": LOW_QUALIFIER_RULE,
            "practicalUseModel": PRACTICAL_USE_MODEL,
            "nativeDecisionUnit": "preflop_first_entry_or_defend_hi_lo",
        },
        "normalization": {
            "packTemplatePath": PACK_TEMPLATE_PATH,
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
                "The normalized candidate converts retained Omaha Hi-Lo article prose into actionable preflop heuristics instead of inventing unsupported exact range charts.",
                "Each heuristic preserves exact paragraph and bullet references so article-derived guidance remains auditable against the retained HTML basis.",
                "Split-pot and eight-or-better qualifier semantics remain explicit in family markers and node fields.",
            ],
        },
        "artifacts": {
            "normalizedPackPath": "pack.json",
            "normalizedManifestPath": "manifest.json",
            "derivedBundlePath": "none",
            "acceptanceReportPath": "none",
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
                    "sha256": pack_sha,
                },
            ],
            "artifactHashes": {
                "retainedBasisSha256": html_sha,
                "transformedIntermediateSha256": intermediate_sha,
                "normalizedPackSha256": pack_sha,
            },
        },
        "promotionAcceptanceChecks": [
            "Exact repo-local file carries the family-native 4-card hi/lo payload.",
            "Exact source path or exact equivalent source reference is retained repo-locally.",
            "Payload markers prove 4-card hi/lo identity through explicit split-pot and low-qualifier semantics.",
            "Normalized artifact preserves the family-native decision unit without unsupported two-card, pushfold, or high-only reduction.",
            "Manifest links retained source basis, transformed intermediate, and normalized artifact through hashes or exact retained-basis linkage.",
        ],
        "notes": [
            "Materialized from the retained Internet Texas Holdem Omaha Hi-Lo article into practical preflop heuristic nodes for an additional cc_hilo / 4-card source.",
            "Selected retained article sections: Key Card, Low Possibilities, High Possibilities.",
            "This source contributes heuristic preflop filters and caveats rather than exact opening charts, so the normalized output stays article-native.",
        ],
    }


def build_candidate_metadata(
    *,
    html_rel: str,
    html_sha: str,
    intermediate_rel: str,
    intermediate_sha: str,
    pack_sha: str,
    candidate_ranges: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "metadataVersion": "1.0",
        "candidateId": CANDIDATE_ID,
        "familyId": FAMILY_ID,
        "familySlug": FAMILY_SLUG,
        "candidateStatus": CANDIDATE_STATUS,
        "currentRepoStatus": "grounded",
        "expectedVerdict": "shape_match_with_grounding_evidence_candidate",
        "packFile": "pack.json",
        "manifestFile": "manifest.json",
        "templateStatus": TEMPLATE_STATUS,
        "groundingDecisionNote": GROUNDING_NOTE,
        "notes": (
            "Materialized from the retained Internet Texas Holdem Omaha Hi-Lo article into practical "
            "preflop heuristic nodes for an additional cc_hilo / 4-card source."
        ),
        "reservedPaths": {
            "sourceDir": "source",
            "intermediateDir": "intermediate",
        },
        "templateSources": {
            "packTemplatePath": PACK_TEMPLATE_PATH,
            "manifestTemplatePath": MANIFEST_TEMPLATE_PATH,
        },
        "materializationSummary": {
            "scriptVersion": SCRIPT_VERSION,
            "nodeCount": len(candidate_ranges),
            "entryCountPerNode": [len(node.get("entries", [])) for node in candidate_ranges],
            "actionableHeuristicCount": sum(len(node.get("entries", [])) for node in candidate_ranges),
            "normalizedPackSha256": pack_sha,
            "retainedSourceStructure": {
                "htmlPath": html_rel,
                "htmlSha256": html_sha,
                "intermediatePath": intermediate_rel,
                "intermediateSha256": intermediate_sha,
            },
            "selectorAxes": selector_axes_from_nodes(candidate_ranges),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-html",
        default=DEFAULT_SOURCE_HTML,
        help="Path to the retained HTML source. Defaults to the URL-downloaded /tmp HTML path.",
    )
    parser.add_argument(
        "--candidate-dir",
        default=DEFAULT_CANDIDATE_DIR,
        help="Candidate directory to create. Defaults to the repo-local cc_hilo / 4-card staging path.",
    )
    parser.add_argument(
        "--retrieved-at",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        help="Retrieval timestamp for the retained source. Defaults to now in UTC.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    source_html_path = resolve_path(args.source_html, root)
    candidate_dir = resolve_path(args.candidate_dir, root)

    if not source_html_path.is_file():
        raise FileNotFoundError(f"source HTML not found: {source_html_path}")
    source_dir = candidate_dir / "source"
    intermediate_dir = candidate_dir / "intermediate"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(exist_ok=True)
    intermediate_dir.mkdir(exist_ok=True)

    retained_name = "internettexasholdem_omaha_hi_lo_starting_hand_strategy_look_fors.html"
    retained_html_path = source_dir / retained_name
    shutil.copyfile(source_html_path, retained_html_path)

    html_rel = str(retained_html_path.relative_to(candidate_dir)).replace("\\", "/")
    html_sha = sha256_file(retained_html_path)
    html_text = retained_html_path.read_text(encoding="utf-8")
    parsed = parse_article_sections(html_text)

    intermediate_path = intermediate_dir / "article_sections.json"
    intermediate = build_intermediate_payload(parsed=parsed, html_rel=html_rel, html_sha=html_sha)
    write_json(intermediate_path, intermediate)
    intermediate_rel = str(intermediate_path.relative_to(candidate_dir)).replace("\\", "/")
    intermediate_sha = sha256_file(intermediate_path)

    candidate_ranges = build_candidate_ranges(
        parsed=parsed,
        html_rel=html_rel,
        html_sha=html_sha,
        intermediate_rel=intermediate_rel,
    )

    pack = build_pack(candidate_ranges=candidate_ranges, source_reference=SOURCE_REFERENCE)
    pack_path = candidate_dir / "pack.json"
    write_json(pack_path, pack)
    pack_sha = sha256_file(pack_path)

    manifest = build_manifest(
        html_rel=html_rel,
        html_sha=html_sha,
        retrieved_at=args.retrieved_at,
        intermediate_rel=intermediate_rel,
        intermediate_sha=intermediate_sha,
        pack_sha=pack_sha,
    )
    manifest_path = candidate_dir / "manifest.json"
    write_json(manifest_path, manifest)

    candidate = build_candidate_metadata(
        html_rel=html_rel,
        html_sha=html_sha,
        intermediate_rel=intermediate_rel,
        intermediate_sha=intermediate_sha,
        pack_sha=pack_sha,
        candidate_ranges=candidate_ranges,
    )
    candidate_path = candidate_dir / "candidate.json"
    write_json(candidate_path, candidate)

    json.dump(
        {
            "status": "ok",
            "scriptVersion": SCRIPT_VERSION,
            "candidateId": CANDIDATE_ID,
            "candidateDir": str(candidate_dir),
            "articleTitle": parsed["articleTitle"],
            "selectedHeadings": [section["heading"] for section in parsed["sections"]],
            "htmlPath": html_rel,
            "htmlSha256": html_sha,
            "intermediatePath": intermediate_rel,
            "intermediateSha256": intermediate_sha,
            "packSha256": pack_sha,
            "filesWritten": [
                str(candidate_path),
                str(pack_path),
                str(manifest_path),
                str(intermediate_path),
                str(retained_html_path),
            ],
        },
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
