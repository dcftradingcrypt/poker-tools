#!/usr/bin/env python3
"""Strict leaf-by-leaf equivalence audit for grounded cc_high / 2-card packs.

This verifier compares each normalized private pack leaf against the matching
derived public bundle leaf for the visible grounded variants only. It is
deliberately narrower and stricter than the bundle builder logic in
scripts/private_pack_ui_server.py:

- it supports only the shorthand syntax actually observed in the grounded packs
- it fails closed on unknown notation instead of silently dropping tokens
- it keeps exact semantics, ordered membership, deduplicated membership, and
  materially lossy cases separate
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "assets/pushfold/aof-bundle.v1.json"

RANKS = "AKQJT98765432"
RANK_INDEX = {rank: idx for idx, rank in enumerate(RANKS)}


def build_valid_categories() -> list[str]:
    categories: list[str] = []
    for i, high in enumerate(RANKS):
        categories.append(high + high)
        for low in RANKS[i + 1 :]:
            categories.append(f"{high}{low}s")
            categories.append(f"{high}{low}o")
    return categories


VALID_CATEGORIES = build_valid_categories()
VALID_CATEGORY_SET = set(VALID_CATEGORIES)
CLASSIFICATION_VOCABULARY = (
    "exact_verbatim_match",
    "exact_ordered_membership_match",
    "membership_equivalent_after_normalization",
    "materially_lossy",
    "insufficient_to_prove",
)


@dataclass(frozen=True)
class VariantConfig:
    variant: str
    regime_id: str
    native_schema: str
    pack_path: Path
    manifest_path: Path


VARIANTS: tuple[VariantConfig, ...] = (
    VariantConfig(
        variant="antes0 (base 9max first-in)",
        regime_id="antes0",
        native_schema="ranges[bb][position]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data/manifest.json",
    ),
    VariantConfig(
        variant="antes10",
        regime_id="antes10",
        native_schema="ranges[bb][position]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes10/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes10/manifest.json",
    ),
    VariantConfig(
        variant="antes12_5",
        regime_id="antes12_5",
        native_schema="ranges[bb][position]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes12_5/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes12_5/manifest.json",
    ),
    VariantConfig(
        variant="antes20",
        regime_id="antes20",
        native_schema="ranges[bb][position]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes20/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/antes20/manifest.json",
    ),
    VariantConfig(
        variant="tool10max_bb100_openjam",
        regime_id="tool10max_bb100_openjam",
        native_schema="ranges[bb][position]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/tool10max_bb100_openjam/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/tool10max_bb100_openjam/manifest.json",
    ),
    VariantConfig(
        variant="tool10max_bb100_call",
        regime_id="tool10max_bb100_call",
        native_schema="ranges[bb][jammer][caller]",
        pack_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/tool10max_bb100_call/pack.json",
        manifest_path=REPO_ROOT / "out/_private/pushfold_real_data_regimes/tool10max_bb100_call/manifest.json",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default=str(BUNDLE_PATH))
    parser.add_argument("--indent", type=int, default=2)
    parser.add_argument("--format", choices=("audit-json", "safety-manifest", "runtime-safety-asset"), default="audit-json")
    parser.add_argument("--output", default="")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def split_range_tokens(raw_value: str) -> list[str]:
    return [token.strip() for token in re.split(r"[\s,;]+", raw_value or "") if token.strip()]


def normalize_any_two(raw_value: str) -> str:
    normalized = re.sub(r"\bAny\s*,\s*two\b", "AnyTwo", raw_value, flags=re.IGNORECASE)
    return re.sub(r"\bAny\s+two\b", "AnyTwo", normalized, flags=re.IGNORECASE)


def split_percentage_prefix(raw_value: str) -> tuple[str | None, str]:
    match = re.match(r"^\s*(\d+(?:\.\d+)?)%\s*(?:,\s*)?(.*)$", raw_value or "")
    if not match:
        return None, raw_value.strip()
    return match.group(1), match.group(2).strip()


def expand_pair_plus(rank: str) -> list[str]:
    start_idx = RANK_INDEX[rank]
    return [RANKS[idx] * 2 for idx in range(start_idx, -1, -1)]


def expand_pair_range(start_rank: str, end_rank: str) -> list[str]:
    start_idx = RANK_INDEX[start_rank]
    end_idx = RANK_INDEX[end_rank]
    if start_idx < end_idx:
        return [RANKS[idx] * 2 for idx in range(start_idx, end_idx + 1)]
    if start_idx == end_idx:
        return [start_rank * 2]
    raise ValueError(f"invalid descending pair range {start_rank}{start_rank}-{end_rank}{end_rank}")


def expand_same_high_plus(high: str, low: str, suitedness: str) -> list[str]:
    high_idx = RANK_INDEX[high]
    low_idx = RANK_INDEX[low]
    if low_idx <= high_idx:
        raise ValueError(f"invalid same-high plus token {high}{low}{suitedness}+")
    return [f"{high}{RANKS[idx]}{suitedness}" for idx in range(low_idx, high_idx, -1)]


def expand_same_high_range(high: str, start_low: str, end_low: str, suitedness: str) -> list[str]:
    high_idx = RANK_INDEX[high]
    start_idx = RANK_INDEX[start_low]
    end_idx = RANK_INDEX[end_low]
    if start_idx <= high_idx or end_idx <= high_idx or end_idx < start_idx:
        raise ValueError(f"invalid same-high range token {high}{start_low}{suitedness}-{high}{end_low}{suitedness}")
    return [f"{high}{RANKS[idx]}{suitedness}" for idx in range(start_idx, end_idx + 1)]


def expand_x_plus(high: str) -> list[str]:
    high_floor_idx = RANK_INDEX[high]
    categories: list[str] = []
    for high_idx in range(high_floor_idx, -1, -1):
        high_rank = RANKS[high_idx]
        for low_idx in range(len(RANKS) - 1, high_idx, -1):
            low_rank = RANKS[low_idx]
            categories.append(f"{high_rank}{low_rank}s")
            categories.append(f"{high_rank}{low_rank}o")
    return categories


def expand_fixed_x(low: str) -> list[str]:
    low_idx = RANK_INDEX[low]
    categories: list[str] = []
    for high_idx in range(0, low_idx):
        high_rank = RANKS[high_idx]
        categories.append(f"{high_rank}{low}s")
        categories.append(f"{high_rank}{low}o")
    return categories


def expand_token(token: str) -> list[str]:
    if token == "AnyTwo":
        return VALID_CATEGORIES[:]
    if token in VALID_CATEGORY_SET:
        return [token]

    pair_plus_match = re.fullmatch(r"([AKQJT98765432])\1\+", token)
    if pair_plus_match:
        return expand_pair_plus(pair_plus_match.group(1))

    pair_range_match = re.fullmatch(r"([AKQJT98765432])\1-([AKQJT98765432])\2", token)
    if pair_range_match:
        return expand_pair_range(pair_range_match.group(1), pair_range_match.group(2))

    same_high_plus_match = re.fullmatch(r"([AKQJT98765432])([AKQJT98765432])(s|o)\+", token)
    if same_high_plus_match:
        return expand_same_high_plus(
            same_high_plus_match.group(1),
            same_high_plus_match.group(2),
            same_high_plus_match.group(3),
        )

    same_high_range_match = re.fullmatch(r"([AKQJT98765432])([AKQJT98765432])(s|o)-\1([AKQJT98765432])\3", token)
    if same_high_range_match:
        return expand_same_high_range(
            same_high_range_match.group(1),
            same_high_range_match.group(2),
            same_high_range_match.group(4),
            same_high_range_match.group(3),
        )

    x_plus_match = re.fullmatch(r"([AKQJT98765432])x\+", token)
    if x_plus_match:
        return expand_x_plus(x_plus_match.group(1))

    fixed_x_match = re.fullmatch(r"([AKQJT98765432])x", token)
    if fixed_x_match:
        return expand_fixed_x(fixed_x_match.group(1))

    raise ValueError(f"unsupported token {token!r}")


def dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def parse_normalized_leaf(raw_value: str) -> dict[str, Any]:
    percentage_prefix, body = split_percentage_prefix(raw_value)
    body = normalize_any_two(body)
    tokens = split_range_tokens(body)
    expanded: list[str] = []
    token_shapes: list[str] = []
    for token in tokens:
        expanded_values = expand_token(token)
        expanded.extend(expanded_values)
        token_shapes.append(token)
    return {
        "raw_value": raw_value,
        "percentage_prefix": percentage_prefix,
        "tokens": tokens,
        "token_shapes": token_shapes,
        "expanded": expanded,
        "deduped": dedupe_preserving_order(expanded),
    }


def normalize_bundle_leaf(bundle_leaf: Any) -> list[str]:
    if not isinstance(bundle_leaf, list) or not all(isinstance(item, str) for item in bundle_leaf):
        raise TypeError("bundle leaf is not list[str]")
    return list(bundle_leaf)


def leaf_lookup_key(variant: VariantConfig, stack_key: str, primary: str, secondary: str | None) -> str:
    if variant.native_schema == "ranges[bb][position]":
        return f"(stack={stack_key}, position={primary})"
    return f"(stack={stack_key}, jammer={primary}, caller={secondary})"


def build_leaf_note(comparison_class: str, bundle_membership_safe: bool, loss_modes: list[str]) -> str:
    if comparison_class == "exact_verbatim_match":
        return "Bundle leaf is exact-contract-equivalent to the normalized pack leaf."
    if comparison_class == "exact_ordered_membership_match":
        return "Bundle preserves ordered membership after shorthand expansion; normalized pack remains exact-semantic authority."
    if comparison_class == "membership_equivalent_after_normalization":
        return "Bundle preserves membership only after normalization of the normalized-pack leaf."
    if comparison_class == "insufficient_to_prove":
        return "Verifier could not prove safe bundle use for this leaf."
    if bundle_membership_safe:
        return "Bundle preserves membership for this leaf but loses exact source semantics."
    if loss_modes:
        membership_affecting = [mode for mode in loss_modes if mode in ("bundle_missing_membership", "bundle_added_membership", "unsupported_notation_or_shape")]
        other_loss_modes = [mode for mode in loss_modes if mode not in membership_affecting]
        if membership_affecting and other_loss_modes:
            return (
                "Bundle is not safe for membership lookup; "
                f"membership-affecting loss modes: {', '.join(membership_affecting)}; "
                f"additional exact-semantic loss modes: {', '.join(other_loss_modes)}."
            )
        if membership_affecting:
            return f"Bundle is not safe for membership lookup; membership-affecting loss modes: {', '.join(membership_affecting)}."
        return f"Bundle is not safe for membership lookup; exact loss modes present: {', '.join(loss_modes)}."
    return "Bundle is not safe for membership lookup for this leaf."


def classify_leaf(variant: VariantConfig, stack_key: str, primary: str, secondary: str | None, raw_leaf: str, bundle_leaf: Any) -> dict[str, Any]:
    lookup_key = leaf_lookup_key(variant, stack_key, primary, secondary)
    schema_path = variant.native_schema
    bundle_regime_key = f"regimes.{variant.regime_id}.catalog"
    try:
        parsed = parse_normalized_leaf(raw_leaf)
        bundle_values = normalize_bundle_leaf(bundle_leaf)
    except Exception as exc:  # noqa: BLE001
        loss_modes = ["unsupported_notation_or_shape"]
        return {
            "variant_or_regime": variant.variant,
            "schema_path": schema_path,
            "native_schema": schema_path,
            "lookup_key_tuple": lookup_key,
            "normalized_leaf": raw_leaf,
            "bundle_leaf": bundle_leaf,
            "comparison_class": "insufficient_to_prove",
            "bundle_membership_safe": False,
            "exact_semantics_authority": "normalized_pack",
            "normalized_pack_path": str(variant.pack_path),
            "bundle_regime_key": bundle_regime_key,
            "normalization_steps": ["parse_failed"],
            "normalization_steps_required": "parse_failed",
            "order_preserved_yes_no": "no",
            "membership_preserved_yes_no": "unknown",
            "exact_loss_mode": str(exc),
            "evidence_paths": [str(variant.pack_path), str(variant.manifest_path), str(BUNDLE_PATH)],
            "percentage_prefix": None,
            "loss_modes": loss_modes,
            "note": build_leaf_note("insufficient_to_prove", False, loss_modes),
        }

    expanded = parsed["expanded"]
    deduped = parsed["deduped"]
    percentage_prefix = parsed["percentage_prefix"]
    bundle_set = set(bundle_values)
    deduped_set = set(deduped)
    exact_verbatim = raw_leaf == bundle_values
    exact_ordered_membership = percentage_prefix is None and expanded == bundle_values
    membership_preserved = deduped_set == bundle_set
    order_preserved = deduped == bundle_values
    has_overlap = len(expanded) != len(deduped)

    normalization_steps: list[str] = []
    if parsed["tokens"]:
        normalization_steps.append("expand_shorthand_to_categories")
    if has_overlap:
        normalization_steps.append("deduplicate_overlap")
    if percentage_prefix is not None:
        normalization_steps.append("drop_percentage_prefix")
    if membership_preserved and not order_preserved:
        normalization_steps.append("reorder_membership")

    if exact_verbatim:
        comparison_class = "exact_verbatim_match"
        loss_modes: list[str] = []
    elif exact_ordered_membership:
        comparison_class = "exact_ordered_membership_match"
        loss_modes = []
    elif percentage_prefix is None and membership_preserved:
        comparison_class = "membership_equivalent_after_normalization"
        loss_modes = ["deduped_overlap_only"] if has_overlap and order_preserved else []
        if not order_preserved:
            loss_modes.append("bundle_reordered_membership")
    else:
        comparison_class = "materially_lossy"
        loss_modes = []
        if percentage_prefix is not None:
            loss_modes.append("dropped_percentage_prefix")
        if has_overlap:
            loss_modes.append("deduped_overlap")
        missing_membership = [value for value in deduped if value not in bundle_set]
        added_membership = [value for value in bundle_values if value not in deduped_set]
        if missing_membership:
            loss_modes.append("bundle_missing_membership")
        if added_membership:
            loss_modes.append("bundle_added_membership")
        if membership_preserved and not order_preserved:
            loss_modes.append("bundle_reordered_membership")
        if not loss_modes:
            loss_modes.append("unclassified_difference")

    bundle_membership_safe = membership_preserved
    exact_semantics_authority = "normalized_pack_and_bundle" if comparison_class == "exact_verbatim_match" else "normalized_pack"

    return {
        "variant_or_regime": variant.variant,
        "schema_path": schema_path,
        "native_schema": schema_path,
        "lookup_key_tuple": lookup_key,
        "normalized_leaf": raw_leaf,
        "bundle_leaf": bundle_values,
        "comparison_class": comparison_class,
        "bundle_membership_safe": bundle_membership_safe,
        "exact_semantics_authority": exact_semantics_authority,
        "normalized_pack_path": str(variant.pack_path),
        "bundle_regime_key": bundle_regime_key,
        "normalization_steps": normalization_steps,
        "normalization_steps_required": ", ".join(normalization_steps) if normalization_steps else "none",
        "order_preserved_yes_no": "yes" if order_preserved else "no",
        "membership_preserved_yes_no": "yes" if membership_preserved else "no",
        "exact_loss_mode": " + ".join(loss_modes) if loss_modes else "none",
        "evidence_paths": [str(variant.pack_path), str(variant.manifest_path), str(BUNDLE_PATH)],
        "percentage_prefix": percentage_prefix,
        "loss_modes": loss_modes,
        "note": build_leaf_note(comparison_class, bundle_membership_safe, loss_modes),
    }


def iter_variant_leaves(variant: VariantConfig, pack: dict[str, Any], bundle_regime: dict[str, Any]) -> list[dict[str, Any]]:
    positions = [str(value) for value in pack.get("positions", []) if isinstance(value, str)]
    stack_keys = [str(value) for value in pack.get("stacksBb", [])]
    ranges = pack.get("ranges", {}) if isinstance(pack.get("ranges"), dict) else {}
    bundle_catalog = bundle_regime.get("catalog", {}) if isinstance(bundle_regime.get("catalog"), dict) else {}
    secondary_positions = (
        pack.get("secondaryPositionsByPosition", {})
        if isinstance(pack.get("secondaryPositionsByPosition"), dict)
        else {}
    )
    results: list[dict[str, Any]] = []

    for stack_key in stack_keys:
        stack_ranges = ranges.get(stack_key, {})
        bundle_stack = bundle_catalog.get(stack_key, {})
        if not isinstance(stack_ranges, dict) or not isinstance(bundle_stack, dict):
            raise TypeError(f"unexpected stack shape for {variant.variant} stack {stack_key}")
        for primary in positions:
            raw_leaf = stack_ranges.get(primary)
            bundle_leaf = bundle_stack.get(primary)
            if variant.native_schema == "ranges[bb][position]":
                if not isinstance(raw_leaf, str):
                    raise TypeError(f"expected string leaf at {variant.variant} {stack_key}/{primary}")
                results.append(classify_leaf(variant, stack_key, primary, None, raw_leaf, bundle_leaf))
                continue

            if not isinstance(raw_leaf, dict) or not isinstance(bundle_leaf, dict):
                raise TypeError(f"expected nested caller map at {variant.variant} {stack_key}/{primary}")
            secondary_for_primary = secondary_positions.get(primary, [])
            if not isinstance(secondary_for_primary, list):
                raise TypeError(f"invalid secondary position map at {variant.variant} {primary}")
            ordered_secondary = [secondary for secondary in secondary_for_primary if isinstance(secondary, str) and secondary in raw_leaf]
            remaining_secondary = [secondary for secondary in raw_leaf.keys() if secondary not in ordered_secondary]
            for secondary in ordered_secondary + remaining_secondary:
                secondary_raw_leaf = raw_leaf.get(secondary)
                secondary_bundle_leaf = bundle_leaf.get(secondary)
                if not isinstance(secondary_raw_leaf, str):
                    raise TypeError(f"expected string leaf at {variant.variant} {stack_key}/{primary}/{secondary}")
                results.append(
                    classify_leaf(
                        variant,
                        stack_key,
                        primary,
                        secondary,
                        secondary_raw_leaf,
                        secondary_bundle_leaf,
                    )
                )
    return results


def choose_example(leaves: list[dict[str, Any]], comparison_class: str, exact_loss_mode: str | None = None) -> dict[str, Any] | None:
    for leaf in leaves:
        if leaf["comparison_class"] != comparison_class:
            continue
        if exact_loss_mode is not None and exact_loss_mode not in leaf["exact_loss_mode"]:
            continue
        return leaf
    return None


def summarize_variant(variant: VariantConfig, leaves: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(leaf["comparison_class"] for leaf in leaves)
    loss_mode_counts = Counter()
    for leaf in leaves:
        loss_mode_counts.update(leaf["loss_modes"])

    representative_examples: list[dict[str, Any]] = []
    for class_name in (
        "membership_equivalent_after_normalization",
        "materially_lossy",
        "insufficient_to_prove",
    ):
        example = choose_example(leaves, class_name)
        if example is not None:
            representative_examples.append(example)
    for loss_mode in ("bundle_missing_membership", "dropped_percentage_prefix", "deduped_overlap_only", "deduped_overlap"):
        example = choose_example(leaves, "materially_lossy", loss_mode)
        if example is None:
            example = choose_example(leaves, "membership_equivalent_after_normalization", loss_mode)
        if example is not None and example not in representative_examples:
            representative_examples.append(example)

    return {
        "variant_or_regime": variant.variant,
        "native_schema": variant.native_schema,
        "total_leaf_count": len(leaves),
        "exact_verbatim_match_count": counts["exact_verbatim_match"],
        "exact_ordered_membership_match_count": counts["exact_ordered_membership_match"],
        "membership_equivalent_after_normalization_count": counts["membership_equivalent_after_normalization"],
        "materially_lossy_count": counts["materially_lossy"],
        "insufficient_to_prove_count": counts["insufficient_to_prove"],
        "bundle_membership_safe_leaf_count": sum(1 for leaf in leaves if leaf["bundle_membership_safe"]),
        "representative_loss_modes": dict(sorted(loss_mode_counts.items())),
        "authoritative_source_rule": (
            "normalized pack remains authoritative for exact semantics"
            if counts["exact_verbatim_match"] != len(leaves)
            else "normalized pack and bundle are exact-contract-equivalent for every leaf"
        ),
        "evidence_paths": [str(variant.pack_path), str(variant.manifest_path), str(BUNDLE_PATH)],
        "representative_examples": representative_examples,
    }


def build_audit_payload(summaries: list[dict[str, Any]], representative_rows: list[dict[str, Any]], leaf_totals: Counter[str]) -> dict[str, Any]:
    return {
        "repo_root": str(REPO_ROOT),
        "parser_basis": {
            "strategy": "new_strict_verifier",
            "cross_checked_against": "scripts/private_pack_ui_server.py",
            "fail_closed_on_unknown_syntax": True,
            "supported_token_forms": [
                "exact_category",
                "pair_plus",
                "pair_range",
                "same_high_plus",
                "same_high_range",
                "x_plus",
                "fixed_x",
                "Any two",
                "leading_percentage_prefix",
            ],
        },
        "variant_results": summaries,
        "representative_non_exact_rows": representative_rows,
        "global_leaf_class_totals": dict(sorted(leaf_totals.items())),
    }


def build_manifest_leaf_record(leaf: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant_or_regime": leaf["variant_or_regime"],
        "native_schema": leaf["native_schema"],
        "lookup_key_tuple": leaf["lookup_key_tuple"],
        "comparison_class": leaf["comparison_class"],
        "bundle_membership_safe": leaf["bundle_membership_safe"],
        "exact_semantics_authority": leaf["exact_semantics_authority"],
        "normalized_pack_path": leaf["normalized_pack_path"],
        "bundle_regime_key": leaf["bundle_regime_key"],
        "normalization_steps_required": leaf["normalization_steps"],
        "loss_modes": leaf["loss_modes"],
        "note": leaf["note"],
    }


def build_safety_manifest(variant_payloads: list[dict[str, Any]], leaf_totals: Counter[str]) -> dict[str, Any]:
    total_leaf_count = sum(payload["summary"]["total_leaf_count"] for payload in variant_payloads)
    bundle_membership_safe_leaf_count = sum(payload["summary"]["bundle_membership_safe_leaf_count"] for payload in variant_payloads)
    generated_from_variants = [
        {
            "variant_or_regime": payload["summary"]["variant_or_regime"],
            "normalized_pack_path": str(payload["variant"].pack_path),
            "manifest_path": str(payload["variant"].manifest_path),
            "bundle_regime_key": f"regimes.{payload['variant'].regime_id}",
        }
        for payload in variant_payloads
    ]
    return {
        "family_id_or_label": "cc_high / 2-card",
        "generated_at_utc": utc_now_iso(),
        "generated_from": {
            "script": str(REPO_ROOT / "scripts/audit_cc_high_2card_bundle_equivalence.py"),
            "bundle_path": str(BUNDLE_PATH),
            "cross_checked_against": str(REPO_ROOT / "scripts/private_pack_ui_server.py"),
            "alignment_artifacts": [
                str(REPO_ROOT / "out/_codex/cc_high_2card_bundle_equivalence_audit.md"),
                str(REPO_ROOT / "out/_codex/cc_high_2card_bundle_semantic_delta.md"),
                str(REPO_ROOT / "out/_codex/cc_high_2card_payload_contract.md"),
            ],
            "variant_inputs": generated_from_variants,
        },
        "variants": [
            {
                "variant_or_regime": payload["summary"]["variant_or_regime"],
                "native_schema": payload["summary"]["native_schema"],
                "total_leaf_count": payload["summary"]["total_leaf_count"],
                "exact_verbatim_match_count": payload["summary"]["exact_verbatim_match_count"],
                "exact_ordered_membership_match_count": payload["summary"]["exact_ordered_membership_match_count"],
                "membership_equivalent_after_normalization_count": payload["summary"]["membership_equivalent_after_normalization_count"],
                "materially_lossy_count": payload["summary"]["materially_lossy_count"],
                "insufficient_to_prove_count": payload["summary"]["insufficient_to_prove_count"],
                "bundle_membership_safe_leaf_count": payload["summary"]["bundle_membership_safe_leaf_count"],
                "leaf_records": [build_manifest_leaf_record(leaf) for leaf in payload["leaves"]],
            }
            for payload in variant_payloads
        ],
        "summary": {
            "total_leaf_count": total_leaf_count,
            "exact_verbatim_match_count": leaf_totals["exact_verbatim_match"],
            "exact_ordered_membership_match_count": leaf_totals["exact_ordered_membership_match"],
            "membership_equivalent_after_normalization_count": leaf_totals["membership_equivalent_after_normalization"],
            "materially_lossy_count": leaf_totals["materially_lossy"],
            "insufficient_to_prove_count": leaf_totals["insufficient_to_prove"],
            "bundle_membership_safe_leaf_count": bundle_membership_safe_leaf_count,
            "classification_vocabulary": list(CLASSIFICATION_VOCABULARY),
            "consumer_authority_rule": "normalized_pack remains authoritative for exact semantics unless exact-contract-equivalence is proven for a leaf",
            "bundle_membership_rule": "bundle_membership_safe is true only where the verifier proved membership preservation",
        },
    }


def build_runtime_safety_asset(variant_payloads: list[dict[str, Any]], leaf_totals: Counter[str]) -> dict[str, Any]:
    regime_payloads: dict[str, dict[str, Any]] = {}
    total_unsafe_leaf_count = 0
    total_safe_leaf_count = 0
    for payload in variant_payloads:
        variant: VariantConfig = payload["variant"]
        leaves = payload["leaves"]
        unsafe_lookup_keys: dict[str, dict[str, Any]] = {}
        unsafe_leaf_count = 0
        safe_leaf_count = 0
        for leaf in leaves:
            if leaf["bundle_membership_safe"]:
                safe_leaf_count += 1
                continue
            unsafe_leaf_count += 1
            stack_match = re.match(r"^\(stack=([^,]+),\s*(?:position|jammer)=([^\),]+)(?:,\s*caller=([^\)]+))?\)$", leaf["lookup_key_tuple"])
            if not stack_match:
                raise ValueError(f"unsupported lookup tuple for runtime safety asset: {leaf['lookup_key_tuple']}")
            stack_key = stack_match.group(1)
            primary_position = stack_match.group(2)
            secondary_position = stack_match.group(3)
            lookup_key = f"{stack_key}|{primary_position}" if secondary_position is None else f"{stack_key}|{primary_position}|{secondary_position}"
            unsafe_lookup_keys[lookup_key] = {
                "lookupKeyTuple": leaf["lookup_key_tuple"],
                "comparisonClass": leaf["comparison_class"],
                "bundleMembershipSafe": False,
                "exactSemanticsAuthority": leaf["exact_semantics_authority"],
                "lossModes": leaf["loss_modes"],
                "note": leaf["note"],
            }
        total_unsafe_leaf_count += unsafe_leaf_count
        total_safe_leaf_count += safe_leaf_count
        regime_payloads[variant.regime_id] = {
            "variantLabel": variant.variant,
            "nativeSchema": variant.native_schema,
            "unsafeLeafCount": unsafe_leaf_count,
            "safeLeafCount": safe_leaf_count,
            "unsafeLookupKeys": unsafe_lookup_keys,
        }

    return {
        "assetVersion": "1.0",
        "familyIdOrLabel": "cc_high / 2-card",
        "generatedAtUtc": utc_now_iso(),
        "generatedFrom": {
            "script": str(REPO_ROOT / "scripts/audit_cc_high_2card_bundle_equivalence.py"),
            "bundlePath": str(BUNDLE_PATH),
            "sourceSafetyManifest": str(REPO_ROOT / "out/_codex/cc_high_2card_bundle_safety_manifest.json"),
        },
        "defaultBundleMembershipSafe": True,
        "classificationVocabulary": list(CLASSIFICATION_VOCABULARY),
        "summary": {
            "totalLeafCount": sum(payload["summary"]["total_leaf_count"] for payload in variant_payloads),
            "safeLeafCount": total_safe_leaf_count,
            "unsafeLeafCount": total_unsafe_leaf_count,
            "exactVerbatimMatchCount": leaf_totals["exact_verbatim_match"],
            "exactOrderedMembershipMatchCount": leaf_totals["exact_ordered_membership_match"],
            "membershipEquivalentAfterNormalizationCount": leaf_totals["membership_equivalent_after_normalization"],
            "materiallyLossyCount": leaf_totals["materially_lossy"],
            "insufficientToProveCount": leaf_totals["insufficient_to_prove"],
            "consumerAuthorityRule": "normalized_pack remains authoritative for exact semantics unless exact-contract-equivalence is proven for a leaf",
            "bundleMembershipRule": "default safe unless the concrete lookup tuple appears in regimes.*.unsafeLookupKeys",
        },
        "regimes": regime_payloads,
    }


def main() -> int:
    args = parse_args()
    bundle = load_json(Path(args.bundle))
    bundle_regimes = bundle.get("regimes", {}) if isinstance(bundle, dict) else {}
    if not isinstance(bundle_regimes, dict):
        raise TypeError("bundle regimes payload is missing or invalid")

    summaries: list[dict[str, Any]] = []
    representative_rows: list[dict[str, Any]] = []
    leaf_totals: Counter[str] = Counter()
    variant_payloads: list[dict[str, Any]] = []

    for variant in VARIANTS:
        pack = load_json(variant.pack_path)
        bundle_regime = bundle_regimes.get(variant.regime_id)
        if not isinstance(bundle_regime, dict):
            raise KeyError(f"bundle regime {variant.regime_id!r} missing")
        leaves = iter_variant_leaves(variant, pack, bundle_regime)
        summary = summarize_variant(variant, leaves)
        summaries.append(summary)
        representative_rows.extend(summary["representative_examples"])
        leaf_totals.update([leaf["comparison_class"] for leaf in leaves])
        variant_payloads.append({"variant": variant, "summary": summary, "leaves": leaves})

    if args.format == "safety-manifest":
        payload = build_safety_manifest(variant_payloads, leaf_totals)
    elif args.format == "runtime-safety-asset":
        payload = build_runtime_safety_asset(variant_payloads, leaf_totals)
    else:
        payload = build_audit_payload(summaries, representative_rows, leaf_totals)

    rendered = json.dumps(payload, indent=args.indent, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
