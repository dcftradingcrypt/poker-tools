#!/usr/bin/env python3
import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


RANKS = "AKQJT98765432"
RANK_INDEX = {rank: idx for idx, rank in enumerate(RANKS)}
POSITION_ORDER = ["UTG", "UTG+1", "UTG+2", "UTG+3", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
POSITION_ORDER_INDEX = {position: idx for idx, position in enumerate(POSITION_ORDER)}
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_PATH = REPO_ROOT / "out/_private/pushfold_real_data/pack.json"
DEFAULT_REGIMES_ROOT = REPO_ROOT / "out/_private/pushfold_real_data_regimes"
DEFAULT_SAFETY_ASSET_PATH = REPO_ROOT / "assets/pushfold/aof-bundle-safety.v1.json"
DEFAULT_MIX_DISPLAY_INDEX_PATH = REPO_ROOT / "out/_codex/poker_mix_display_index.json"
DEFAULT_MIX_UI_CATALOG_PATH = REPO_ROOT / "out/_codex/poker_mix_ui_catalog.json"
VALID_CATEGORIES = set()
for i, high in enumerate(RANKS):
    VALID_CATEGORIES.add(high + high)
    for low in RANKS[i + 1 :]:
        VALID_CATEGORIES.add(high + low + "s")
        VALID_CATEGORIES.add(high + low + "o")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--pack", default=str(DEFAULT_PACK_PATH))
    parser.add_argument("--regimes-root", default=str(DEFAULT_REGIMES_ROOT))
    parser.add_argument("--index", default=str(REPO_ROOT / "index.html"))
    parser.add_argument("--safety-asset", default=str(DEFAULT_SAFETY_ASSET_PATH))
    parser.add_argument("--mix-display-index", default=str(DEFAULT_MIX_DISPLAY_INDEX_PATH))
    parser.add_argument("--mix-ui-catalog", default=str(DEFAULT_MIX_UI_CATALOG_PATH))
    parser.add_argument("--export-public-bundle", default="")
    return parser


@lru_cache(maxsize=None)
def load_pack(pack_path: str) -> dict:
    return json.loads(Path(pack_path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_runtime_safety_asset(asset_path: str) -> dict:
    return json.loads(Path(asset_path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_mix_display_index(index_path: str) -> dict:
    return json.loads(Path(index_path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_mix_ui_catalog(catalog_path: str) -> dict:
    return json.loads(Path(catalog_path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_mix_ui_family_bundle(bundle_path: str) -> dict:
    return json.loads(Path(bundle_path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_json_file(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def position_order_index(position: str) -> int:
    return POSITION_ORDER_INDEX.get(str(position).strip(), len(POSITION_ORDER) + 1)


def sort_positions(values) -> list[str]:
    unique = {str(value).strip() for value in values if str(value).strip()}
    return sorted(unique, key=lambda value: (position_order_index(value), value))


def infer_call_role_orientation_from_pairs(position_pairs) -> str:
    jammer_first_count = 0
    caller_first_count = 0
    for first_position, second_position in position_pairs:
        first_index = position_order_index(first_position)
        second_index = position_order_index(second_position)
        if first_index == second_index:
            continue
        if first_index < second_index:
            jammer_first_count += 1
        else:
            caller_first_count += 1
    return "caller_first" if caller_first_count > jammer_first_count else "jammer_first"


def should_invert_call_secondary_positions(secondary_positions_by_position: dict) -> bool:
    position_pairs = [
        (position, secondary_position)
        for position, secondary_positions in secondary_positions_by_position.items()
        if isinstance(secondary_positions, list)
        for secondary_position in secondary_positions
        if str(secondary_position).strip()
    ]
    if not position_pairs:
        return False
    return infer_call_role_orientation_from_pairs(position_pairs) == "caller_first"


def invert_call_secondary_positions_by_position(secondary_positions_by_position: dict) -> dict[str, list[str]]:
    inverted = {}
    for caller, jammers in secondary_positions_by_position.items():
        if not isinstance(jammers, list):
            continue
        for jammer in jammers:
            normalized_jammer = str(jammer).strip()
            normalized_caller = str(caller).strip()
            if not normalized_jammer or not normalized_caller:
                continue
            inverted.setdefault(normalized_jammer, []).append(normalized_caller)
    return {
        position: sort_positions(values)
        for position, values in inverted.items()
    }


def invert_call_catalog(catalog: dict) -> dict:
    inverted = {}
    for bb, raw_positions in catalog.items():
        if not isinstance(raw_positions, dict):
            continue
        inverted_positions = {}
        for caller, raw_jammers in raw_positions.items():
            if not isinstance(raw_jammers, dict):
                continue
            normalized_caller = str(caller).strip()
            if not normalized_caller:
                continue
            for jammer, categories in raw_jammers.items():
                normalized_jammer = str(jammer).strip()
                if not normalized_jammer or not isinstance(categories, list):
                    continue
                inverted_positions.setdefault(normalized_jammer, {})[normalized_caller] = list(categories)
        inverted[bb] = inverted_positions
    return inverted


def should_invert_call_unsafe_lookup_keys(unsafe_lookup_keys: dict) -> bool:
    position_pairs = []
    for lookup_key in unsafe_lookup_keys.keys():
        parts = str(lookup_key).split("|")
        if len(parts) != 3:
            continue
        position_pairs.append((parts[1], parts[2]))
    if not position_pairs:
        return False
    return infer_call_role_orientation_from_pairs(position_pairs) == "caller_first"


def invert_call_unsafe_lookup_keys(unsafe_lookup_keys: dict) -> dict:
    inverted = {}
    for lookup_key, record in unsafe_lookup_keys.items():
        parts = str(lookup_key).split("|")
        if len(parts) != 3:
            inverted[str(lookup_key)] = record
            continue
        bb, caller, jammer = parts
        next_record = dict(record)
        next_record["lookupKeyTuple"] = re.sub(
            r"\(stack=([^,]+),\s*jammer=([^,]+),\s*caller=([^)]+)\)",
            r"(stack=\1, jammer=\3, caller=\2)",
            str(record.get("lookupKeyTuple", "")).strip(),
        )
        inverted[f"{bb}|{jammer}|{caller}"] = next_record
    return inverted


@lru_cache(maxsize=None)
def load_rng_rows_from_archive(zip_path: str, source_path_in_archive: str) -> tuple[dict, ...]:
    archive_path = Path(zip_path)
    with zipfile.ZipFile(archive_path) as zf:
        target_name = next(
            (name for name in zf.namelist() if name.endswith(source_path_in_archive)),
            "",
        )
        if not target_name:
            raise FileNotFoundError(f"source path not found in archive: {source_path_in_archive}")
        lines = zf.read(target_name).decode("utf-8", "replace").splitlines()
    rows = []
    for hand_token, raw_line in zip(lines[0::2], lines[1::2]):
        parts = raw_line.split(";", 1)
        try:
            frequency = float(parts[0])
        except ValueError:
            frequency = 0.0
        try:
            ev_value = float(parts[1]) if len(parts) > 1 else 0.0
        except ValueError:
            ev_value = 0.0
        rows.append(
            {
                "handToken": hand_token,
                "frequency": frequency,
                "evMilliSmallBlind": ev_value,
                "rawLine": raw_line,
            }
        )
    rows.sort(key=lambda row: (-row["frequency"], -row["evMilliSmallBlind"], row["handToken"]))
    return tuple(rows)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json_file(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_range_tokens(raw_value: str) -> list[str]:
    return [token.strip() for token in re.split(r"[\s,;]+", raw_value or "") if token.strip()]


def expand_pair_plus(rank: str) -> list[str]:
    start_idx = RANK_INDEX[rank]
    return [RANKS[idx] * 2 for idx in range(start_idx, -1, -1)]


def expand_same_high_plus(high: str, low: str, suitedness: str) -> list[str]:
    high_idx = RANK_INDEX[high]
    low_idx = RANK_INDEX[low]
    if low_idx <= high_idx:
        return []
    return [f"{high}{RANKS[idx]}{suitedness}" for idx in range(low_idx, high_idx, -1)]


def expand_same_high_range(high: str, start_low: str, end_low: str, suitedness: str) -> list[str]:
    high_idx = RANK_INDEX[high]
    start_idx = RANK_INDEX[start_low]
    end_idx = RANK_INDEX[end_low]
    if start_idx <= high_idx or end_idx <= high_idx or end_idx < start_idx:
        return []
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


def expand_range_token(token: str) -> list[str]:
    if token in VALID_CATEGORIES:
        return [token]

    pair_plus_match = re.fullmatch(r"([AKQJT98765432])\1\+", token)
    if pair_plus_match:
        return expand_pair_plus(pair_plus_match.group(1))

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

    return []


def parse_categories(raw_value: str) -> list[str]:
    seen = set()
    categories = []
    for token in split_range_tokens(raw_value):
        for category in expand_range_token(token):
            if category in VALID_CATEGORIES and category not in seen:
                seen.add(category)
                categories.append(category)
    return categories


def normalize_ante_slug(raw_value: str) -> str:
    raw_value = str(raw_value or "").strip().lower()
    if not raw_value or raw_value == "0":
        return "0"
    raw_value = raw_value.removesuffix("%")
    raw_value = raw_value.replace(".", "_")
    raw_value = re.sub(r"[^a-z0-9_]+", "_", raw_value)
    raw_value = re.sub(r"_+", "_", raw_value).strip("_")
    return raw_value or "0"


def infer_regime_id(pack: dict, pack_path: Path) -> str:
    meta = pack.get("meta", {}) if isinstance(pack, dict) else {}
    explicit_regime_id = str(meta.get("regimeId", "")).strip()
    if explicit_regime_id:
        return explicit_regime_id
    assumptions = meta.get("assumptions", {}) if isinstance(meta, dict) else {}
    explicit_assumption_regime_id = str(assumptions.get("regimeId", "")).strip()
    if explicit_assumption_regime_id:
        return explicit_assumption_regime_id
    ante_value = normalize_ante_slug(assumptions.get("ante", ""))
    if ante_value:
        return f"antes{ante_value}"
    meta_name = str(meta.get("name", "")).strip().lower()
    match = re.search(r"(antes[a-z0-9_]+)", meta_name)
    if match:
        return match.group(1)
    fallback = re.sub(r"[^a-z0-9_]+", "_", pack_path.parent.name.lower()).strip("_")
    return fallback or "antes0"


def build_regime_label(ante_value: str) -> str:
    if ante_value == "0":
        return "No antes"
    return f"{ante_value} antes"


def build_semantics_payload(pack: dict, regime_id: str, regime_label: str) -> dict:
    meta = pack.get("meta", {}) if isinstance(pack, dict) else {}
    assumptions = meta.get("assumptions", {}) if isinstance(meta, dict) else {}
    ante_value = str(assumptions.get("ante", "")).strip()
    range_mode = str(assumptions.get("rangeMode", "")).strip() or "open_jam"
    source_name = str(meta.get("name", "")).strip()
    source_family = "push72o_tool" if source_name.startswith("push72o_tool_") else "push72o_charts"
    if source_family == "push72o_tool":
        family_id = "push72o_tool_10max_bbante"
        family_label = "10max Push72o tool / BB-ante shove-call"
        family_description = "10max BB-ante tool family. Open-jam and call-vs-jam modes are separate from the 9max Jennifear first-in charts."
        lineage_label = "Push72o push-or-fold tool"
    else:
        family_id = "jennifear_9max_first_in"
        family_label = "9max Jennifear charts / first-in shove"
        family_description = "9max Jennifear first-in shove chart family. This is separate from the 10max Push72o BB-ante tool modes."
        lineage_label = "Jennifear chart family"
    action_label = "call-vs-jam inclusion" if range_mode == "call_vs_jam" else "open-jam inclusion"
    active_label = "call included" if range_mode == "call_vs_jam" else "jam included"
    mode_label = "Call vs jam" if range_mode == "call_vs_jam" else (
        "First-in shove" if "first-in" in str(assumptions.get("spot", "")).strip().lower() else "Open jam"
    )
    position_mode_label = "jammer + caller selectors" if range_mode == "call_vs_jam" else "single position selector"
    return {
        "regimeId": regime_id,
        "regimeLabel": regime_label,
        "familyId": family_id,
        "familyLabel": family_label,
        "familyDescription": family_description,
        "lineageLabel": lineage_label,
        "modeLabel": mode_label,
        "positionModeLabel": position_mode_label,
        "requiresSecondaryPosition": range_mode == "call_vs_jam",
        "viewKind": "binary_category_inclusion",
        "actionLabel": action_label,
        "activeLabel": active_label,
        "weighted": False,
        "table": str(meta.get("table", "")).strip(),
        "model": str(assumptions.get("model") or meta.get("model", "")).strip(),
        "spot": str(assumptions.get("spot", "")).strip(),
        "ante": ante_value,
        "anteType": str(assumptions.get("anteType", "")).strip(),
        "anteSize": str(assumptions.get("anteSize", "")).strip(),
        "sourceBucketAnte": str(assumptions.get("sourceBucketAnte", "")).strip(),
        "rangeMode": range_mode,
        "primaryPositionRole": str(assumptions.get("primaryPositionRole", "position")).strip() or "position",
        "secondaryPositionRole": str(assumptions.get("secondaryPositionRole", "")).strip(),
        "sourceName": source_name,
        "sourceReference": str(meta.get("source", "")).strip(),
        "encodingNote": "source shorthand expanded into exact categories; mixed frequencies are not available",
        "sourceFamily": source_family,
    }


def build_catalog(pack: dict) -> dict:
    stacks = [int(x) for x in pack.get("stacksBb", []) if isinstance(x, (int, float))]
    positions = [str(x) for x in pack.get("positions", []) if isinstance(x, str)]
    ranges = pack.get("ranges", {}) if isinstance(pack, dict) else {}
    meta = pack.get("meta", {}) if isinstance(pack, dict) else {}
    assumptions = meta.get("assumptions", {}) if isinstance(meta, dict) else {}
    range_mode = str(assumptions.get("rangeMode", "")).strip() or "open_jam"
    secondary_positions_by_position = (
        pack.get("secondaryPositionsByPosition", {}) if isinstance(pack.get("secondaryPositionsByPosition", {}), dict) else {}
    )
    catalog = {}
    for bb in stacks:
        raw_positions = ranges.get(str(bb), {})
        if not isinstance(raw_positions, dict):
            continue
        catalog[bb] = {}
        for position in positions:
            raw_value = raw_positions.get(position)
            if isinstance(raw_value, str):
                catalog[bb][position] = parse_categories(raw_value)
            elif isinstance(raw_value, dict):
                catalog[bb][position] = {}
                for secondary_position, secondary_raw_value in raw_value.items():
                    if isinstance(secondary_raw_value, str):
                        catalog[bb][position][str(secondary_position)] = parse_categories(secondary_raw_value)
    normalized_secondary_positions = {
        str(position): [str(value) for value in values if isinstance(value, str)]
        for position, values in secondary_positions_by_position.items()
        if isinstance(values, list)
    }
    normalized_catalog = catalog
    normalized_positions = positions
    if range_mode == "call_vs_jam" and should_invert_call_secondary_positions(normalized_secondary_positions):
        normalized_secondary_positions = invert_call_secondary_positions_by_position(normalized_secondary_positions)
        normalized_catalog = invert_call_catalog(catalog)
        normalized_positions = sort_positions(normalized_secondary_positions.keys())
    return {
        "stacks": stacks,
        "positions": normalized_positions,
        "secondaryPositionsByPosition": normalized_secondary_positions,
        "catalog": normalized_catalog,
    }


def parse_ante_sort_value(ante_value: str) -> float:
    ante_value = str(ante_value or "").strip()
    if ante_value == "0":
        return 0.0
    try:
        return float(ante_value.removesuffix("%"))
    except ValueError:
        return float("inf")


def discover_regime_pack_paths(primary_pack_path: Path, regimes_root: Path) -> list[Path]:
    pack_paths = [primary_pack_path]
    if regimes_root.exists():
        pack_paths.extend(sorted(regimes_root.glob("*/pack.json")))
    return [path for path in pack_paths if path.exists()]


def build_regime_entry(pack_path: Path) -> dict:
    pack = load_pack(str(pack_path))
    regime_id = infer_regime_id(pack, pack_path)
    meta = pack.get("meta", {}) if isinstance(pack, dict) else {}
    ante_value = str(meta.get("assumptions", {}).get("ante", "")).strip()
    regime_label = str(meta.get("regimeLabel", "")).strip() or build_regime_label(ante_value)
    catalog = build_catalog(pack)
    semantics = build_semantics_payload(pack, regime_id, regime_label)
    return {
        "id": regime_id,
        "label": regime_label,
        "sortIndex": int(meta.get("sortIndex", 0)) if str(meta.get("sortIndex", "")).strip().isdigit() else 0,
        "packPath": str(pack_path),
        "stacks": catalog["stacks"],
        "positions": catalog["positions"],
        "secondaryPositionsByPosition": catalog["secondaryPositionsByPosition"],
        "catalog": catalog["catalog"],
        "semantics": semantics,
    }


def build_available_regimes_payload(regimes: dict[str, dict]) -> list[dict]:
    sorted_entries = sorted(
        regimes.values(),
        key=lambda entry: (
            entry.get("sortIndex", 0),
            parse_ante_sort_value(entry["semantics"].get("ante", "")),
            entry["id"],
        ),
    )
    return [
        {
            "id": entry["id"],
            "label": entry["label"],
            "familyId": entry["semantics"].get("familyId", ""),
            "familyLabel": entry["semantics"].get("familyLabel", ""),
            "familyDescription": entry["semantics"].get("familyDescription", ""),
            "lineageLabel": entry["semantics"].get("lineageLabel", ""),
            "ante": entry["semantics"].get("ante", ""),
            "sourceName": entry["semantics"].get("sourceName", ""),
            "sourceFamily": entry["semantics"].get("sourceFamily", ""),
            "table": entry["semantics"].get("table", ""),
            "spot": entry["semantics"].get("spot", ""),
            "modeLabel": entry["semantics"].get("modeLabel", ""),
            "actionLabel": entry["semantics"].get("actionLabel", ""),
            "positionModeLabel": entry["semantics"].get("positionModeLabel", ""),
            "rangeMode": entry["semantics"].get("rangeMode", ""),
            "anteType": entry["semantics"].get("anteType", ""),
            "anteSize": entry["semantics"].get("anteSize", ""),
        }
        for entry in sorted_entries
    ]


def build_app_state(primary_pack_path: str, regimes_root: str) -> dict:
    primary_path = Path(primary_pack_path)
    regimes = {}
    default_regime = None
    for pack_path in discover_regime_pack_paths(primary_path, Path(regimes_root)):
        entry = build_regime_entry(pack_path)
        regimes[entry["id"]] = entry
        if pack_path == primary_path:
            default_regime = entry["id"]
    if not regimes:
        raise RuntimeError(f"no packs discovered from {primary_pack_path}")
    if not default_regime:
        default_regime = next(iter(regimes.keys()))
    return {
        "regimes": regimes,
        "defaultRegime": default_regime,
        "availableRegimes": build_available_regimes_payload(regimes),
    }


def build_public_bundle_payload(primary_pack_path: str, regimes_root: str) -> dict:
    app_state = build_app_state(primary_pack_path, regimes_root)
    bundled_regimes = {}
    for regime_id, entry in app_state["regimes"].items():
        bundled_regimes[regime_id] = {
            "id": entry["id"],
            "label": entry["label"],
            "sortIndex": entry.get("sortIndex", 0),
            "stacks": entry["stacks"],
            "positions": entry["positions"],
            "secondaryPositionsByPosition": entry["secondaryPositionsByPosition"],
            "catalog": entry["catalog"],
            "semantics": entry["semantics"],
        }
    return {
        "bundleVersion": "1.0",
        "generatedAtUtc": utc_now_iso(),
        "bundleKind": "repo_hosted_aof",
        "defaultRegime": app_state["defaultRegime"],
        "availableRegimes": app_state["availableRegimes"],
        "regimes": bundled_regimes,
    }


def build_runtime_safety_state(safety_asset_path: str) -> dict:
    payload = load_runtime_safety_asset(safety_asset_path)
    raw_regimes = payload.get("regimes", {}) if isinstance(payload, dict) else {}
    if not isinstance(raw_regimes, dict):
        raise RuntimeError(f"invalid runtime safety asset: {safety_asset_path}")
    normalized_regimes = {}
    for regime_id, raw_entry in raw_regimes.items():
        if not isinstance(raw_entry, dict):
            continue
        raw_unsafe_lookup_keys = raw_entry.get("unsafeLookupKeys", {})
        if not isinstance(raw_unsafe_lookup_keys, dict):
            raw_unsafe_lookup_keys = {}
        unsafe_lookup_keys = {}
        for lookup_key, raw_record in raw_unsafe_lookup_keys.items():
            if not isinstance(raw_record, dict):
                continue
            unsafe_lookup_keys[str(lookup_key)] = {
                "lookupKeyTuple": str(raw_record.get("lookupKeyTuple", "")).strip(),
                "comparisonClass": str(raw_record.get("comparisonClass", "")).strip() or "materially_lossy",
                "bundleMembershipSafe": raw_record.get("bundleMembershipSafe") is True,
                "exactSemanticsAuthority": str(raw_record.get("exactSemanticsAuthority", "")).strip() or "normalized_pack",
                "lossModes": [str(value).strip() for value in raw_record.get("lossModes", []) if str(value).strip()],
                "note": str(raw_record.get("note", "")).strip(),
            }
        normalized_unsafe_lookup_keys = (
            invert_call_unsafe_lookup_keys(unsafe_lookup_keys)
            if "call" in str(regime_id).lower() and should_invert_call_unsafe_lookup_keys(unsafe_lookup_keys)
            else unsafe_lookup_keys
        )
        normalized_regimes[str(regime_id)] = {
            "variantLabel": str(raw_entry.get("variantLabel", "")).strip() or str(regime_id),
            "nativeSchema": str(raw_entry.get("nativeSchema", "")).strip(),
            "unsafeLookupKeys": normalized_unsafe_lookup_keys,
        }
    return {
        "assetPath": str(safety_asset_path),
        "defaultBundleMembershipSafe": payload.get("defaultBundleMembershipSafe", True) is True,
        "regimes": normalized_regimes,
    }


def build_mix_display_state(index_path: str) -> dict:
    payload = load_mix_display_index(index_path)
    families = payload.get("families", []) if isinstance(payload, dict) else []
    if not isinstance(families, list):
        raise RuntimeError(f"invalid mix display index: {index_path}")
    normalized_payload = dict(payload) if isinstance(payload, dict) else {}
    normalized_payload["assetPath"] = display_path(Path(index_path))
    return normalized_payload


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def build_mix_ui_state(catalog_path: str) -> tuple[dict, dict[str, dict]]:
    payload = load_mix_ui_catalog(catalog_path)
    families = payload.get("families", []) if isinstance(payload, dict) else []
    if not isinstance(families, list):
        raise RuntimeError(f"invalid mix ui catalog: {catalog_path}")
    normalized_catalog = dict(payload) if isinstance(payload, dict) else {}
    normalized_catalog["assetPath"] = display_path(Path(catalog_path))
    bundles: dict[str, dict] = {}
    for raw_family in families:
        if not isinstance(raw_family, dict):
            continue
        family_id = str(raw_family.get("familyId", "")).strip()
        bundle_artifact = str(raw_family.get("bundleArtifact", "")).strip()
        if not family_id or not bundle_artifact:
            continue
        bundle_path = Path(bundle_artifact)
        if not bundle_path.is_absolute():
            bundle_path = REPO_ROOT / bundle_artifact
        bundle_payload = load_mix_ui_family_bundle(str(bundle_path))
        if not isinstance(bundle_payload, dict):
            raise RuntimeError(f"invalid mix ui family bundle: {bundle_path}")
        normalized_bundle = dict(bundle_payload)
        normalized_bundle["assetPath"] = display_path(bundle_path)
        normalized_bundle["bundleArtifact"] = bundle_artifact
        bundles[family_id] = normalized_bundle
    return normalized_catalog, bundles


def read_mix_bundle_spot(bundle_payload: dict, spot_id: str) -> dict | None:
    spots = bundle_payload.get("spots", []) if isinstance(bundle_payload, dict) else []
    if not isinstance(spots, list):
        return None
    for raw_spot in spots:
        if not isinstance(raw_spot, dict):
            continue
        if str(raw_spot.get("spotId", "")).strip() == spot_id:
            return raw_spot
    return None


def build_mix_exact_spot_payload(
    mix_ui_bundles: dict[str, dict],
    *,
    family_id: str,
    spot_id: str,
    page: int,
    page_size: int,
    positive_only: bool,
) -> dict:
    bundle_payload = mix_ui_bundles.get(family_id)
    if not isinstance(bundle_payload, dict):
        raise KeyError("family_unavailable")
    if str(bundle_payload.get("displayClass", "")).strip() != "grounded_exact_display":
        raise ValueError("exact_display_unavailable")
    bundle_artifact = str(bundle_payload.get("bundleArtifact", "")).strip()
    source_pack_path = str(bundle_payload.get("sourcePackPath", "")).strip()
    spot_payload = read_mix_bundle_spot(bundle_payload, spot_id)
    if not isinstance(spot_payload, dict):
        raise KeyError("spot_unavailable")

    resolved_rows: list[dict] = []
    row_mode = "preview_only"
    if family_id == "cc_high / 4-card":
        if not source_pack_path:
            raise FileNotFoundError("source_pack_missing")
        pack_path = REPO_ROOT / source_pack_path
        manifest_path = pack_path.parent / "manifest.json"
        manifest_payload = load_json_file(str(manifest_path))
        retained_basis_path = str(
            manifest_payload.get("source", {}).get("retainedBasisPath", "")
        ).strip()
        if not retained_basis_path:
            raise FileNotFoundError("retained_basis_missing")
        archive_path = (pack_path.parent / retained_basis_path).resolve()
        source_path_in_archive = str(spot_payload.get("sourcePathInArchive", "")).strip()
        if not source_path_in_archive:
            raise FileNotFoundError("source_path_in_archive_missing")
        resolved_rows = [dict(row) for row in load_rng_rows_from_archive(str(archive_path), source_path_in_archive)]
        row_mode = "frequency_ev"
    else:
        pack_path = REPO_ROOT / source_pack_path
        pack_payload = load_json_file(str(pack_path))
        candidate_ranges = pack_payload.get("candidateRanges", []) if isinstance(pack_payload, dict) else []
        exact_range = next(
            (
                raw_range
                for raw_range in candidate_ranges
                if isinstance(raw_range, dict)
                and str(raw_range.get("decisionNodeId", "")).strip() == spot_id
            ),
            None,
        )
        if not isinstance(exact_range, dict):
            raise KeyError("spot_unavailable_in_pack")
        for raw_entry in exact_range.get("entries", []):
            if not isinstance(raw_entry, dict):
                continue
            raw_leaf = raw_entry.get("rawLeaf", {}) if isinstance(raw_entry.get("rawLeaf"), dict) else {}
            resolved_rows.append(
                {
                    "handToken": str(raw_entry.get("handToken", "")).strip(),
                    "inclusionState": str(raw_entry.get("inclusionState", "")).strip(),
                    "sourceValueText": str(raw_leaf.get("sourceValueText", "")).strip(),
                }
            )
        row_mode = "chart_value"

    total_entries = len(resolved_rows)
    if positive_only and row_mode == "frequency_ev":
        filtered_rows = [row for row in resolved_rows if float(row.get("frequency", 0.0)) > 0.0]
    elif positive_only and row_mode == "chart_value":
        filtered_rows = [
            row
            for row in resolved_rows
            if str(row.get("inclusionState", "")).strip().lower() not in {"none", "exclude", "excluded"}
        ]
    else:
        filtered_rows = resolved_rows
    filtered_count = len(filtered_rows)
    normalized_page_size = max(25, min(500, page_size))
    normalized_page = max(1, page)
    page_count = max(1, (filtered_count + normalized_page_size - 1) // normalized_page_size)
    if normalized_page > page_count:
        normalized_page = page_count
    start_index = (normalized_page - 1) * normalized_page_size
    end_index = start_index + normalized_page_size
    page_rows = filtered_rows[start_index:end_index]
    return {
        "ok": True,
        "familyId": family_id,
        "spotId": spot_id,
        "spotLabel": str(spot_payload.get("spotLabel", "")).strip(),
        "displayClass": str(bundle_payload.get("displayClass", "")).strip(),
        "bundleArtifact": bundle_artifact,
        "sourcePackPath": source_pack_path,
        "sourcePathInArchive": str(spot_payload.get("sourcePathInArchive", "")).strip(),
        "rowMode": row_mode,
        "positiveOnly": positive_only,
        "totalEntries": total_entries,
        "filteredEntries": filtered_count,
        "page": normalized_page,
        "pageSize": normalized_page_size,
        "pageCount": page_count,
        "rows": page_rows,
    }


def build_runtime_safety_lookup_key(bb: int, position: str, secondary_position: str = "") -> str:
    return f"{bb}|{position}" if not secondary_position else f"{bb}|{position}|{secondary_position}"


def read_runtime_unsafe_tuple_record(runtime_safety: dict, regime_id: str, bb: int, position: str, secondary_position: str = "") -> dict | None:
    regimes = runtime_safety.get("regimes", {}) if isinstance(runtime_safety, dict) else {}
    regime_entry = regimes.get(regime_id)
    if not isinstance(regime_entry, dict):
        return None
    unsafe_lookup_keys = regime_entry.get("unsafeLookupKeys", {})
    if not isinstance(unsafe_lookup_keys, dict):
        return None
    record = unsafe_lookup_keys.get(build_runtime_safety_lookup_key(bb, position, secondary_position))
    return record if isinstance(record, dict) else None


class PrivatePackUiHandler(BaseHTTPRequestHandler):
    server_version = "PrivatePackUiServer/1.0"

    def log_message(self, format: str, *args) -> None:
        return

    @property
    def app(self) -> dict:
        return self.server.app  # type: ignore[attr-defined]

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path in ("/", "/index.html"):
            self.serve_index()
            return
        if parsed.path == "/api/health":
            payload, status = self.health_payload(query)
            self.serve_json(payload, status)
            return
        if parsed.path == "/api/stacks":
            payload, status = self.stacks_payload(query)
            self.serve_json(payload, status)
            return
        if parsed.path == "/api/stack":
            self.serve_stack_payload(query)
            return
        if parsed.path == "/api/mix-display-index":
            self.serve_json(self.app["mixDisplayIndex"])
            return
        if parsed.path == "/api/mix-ui-catalog":
            self.serve_json(self.app["mixUiCatalog"])
            return
        if parsed.path == "/api/mix-ui-family":
            requested_family = (query.get("familyId") or [""])[0].strip()
            available_families = sorted(self.app["mixUiBundles"].keys())
            if not requested_family:
                self.serve_json(
                    {
                        "ok": False,
                        "status": "family_missing",
                        "availableFamilies": available_families,
                    },
                    HTTPStatus.BAD_REQUEST,
                )
                return
            payload = self.app["mixUiBundles"].get(requested_family)
            if not isinstance(payload, dict):
                self.serve_json(
                    {
                        "ok": False,
                        "status": "family_unavailable",
                        "requestedFamily": requested_family,
                        "availableFamilies": available_families,
                    },
                    HTTPStatus.NOT_FOUND,
                )
                return
            self.serve_json(payload)
            return
        if parsed.path == "/api/mix-exact-spot":
            requested_family = (query.get("familyId") or [""])[0].strip()
            requested_spot = (query.get("spotId") or [""])[0].strip()
            try:
                page = int((query.get("page") or ["1"])[0])
            except ValueError:
                page = 1
            try:
                page_size = int((query.get("pageSize") or ["200"])[0])
            except ValueError:
                page_size = 200
            positive_only_raw = (query.get("positiveOnly") or ["1"])[0].strip().lower()
            positive_only = positive_only_raw not in {"0", "false", "no"}
            if not requested_family:
                self.serve_json({"ok": False, "status": "family_missing"}, HTTPStatus.BAD_REQUEST)
                return
            if not requested_spot:
                self.serve_json({"ok": False, "status": "spot_missing"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                payload = build_mix_exact_spot_payload(
                    self.app["mixUiBundles"],
                    family_id=requested_family,
                    spot_id=requested_spot,
                    page=page,
                    page_size=page_size,
                    positive_only=positive_only,
                )
            except KeyError as err:
                self.serve_json(
                    {
                        "ok": False,
                        "status": str(err).strip("'"),
                        "requestedFamily": requested_family,
                        "requestedSpot": requested_spot,
                    },
                    HTTPStatus.NOT_FOUND,
                )
                return
            except ValueError as err:
                self.serve_json(
                    {
                        "ok": False,
                        "status": str(err),
                        "requestedFamily": requested_family,
                        "requestedSpot": requested_spot,
                    },
                    HTTPStatus.BAD_REQUEST,
                )
                return
            except FileNotFoundError as err:
                self.serve_json(
                    {
                        "ok": False,
                        "status": str(err),
                        "requestedFamily": requested_family,
                        "requestedSpot": requested_spot,
                    },
                    HTTPStatus.NOT_FOUND,
                )
                return
            self.serve_json(payload)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def serve_index(self) -> None:
        body = Path(self.app["index"]).read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            return

    def serve_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            return

    def read_requested_regime_id(self, query: dict) -> str:
        requested_regime = (query.get("regime") or [""])[0].strip()
        return requested_regime or self.app["defaultRegime"]

    def read_selected_regime(self, query: dict) -> tuple[str, dict | None]:
        regime_id = self.read_requested_regime_id(query)
        return regime_id, self.app["regimes"].get(regime_id)

    def build_regime_not_found_payload(self, requested_regime: str) -> dict:
        return {
            "ok": False,
            "status": "regime_unavailable",
            "requestedRegime": requested_regime,
            "defaultRegime": self.app["defaultRegime"],
            "availableRegimes": self.app["availableRegimes"],
        }

    def build_selected_regime_payload(self, entry: dict) -> dict:
        return {
            "selectedRegime": entry["id"],
            "availableRegimes": self.app["availableRegimes"],
            "semantics": entry["semantics"],
        }

    def health_payload(self, query: dict) -> tuple[dict, int]:
        requested_regime, entry = self.read_selected_regime(query)
        if not entry:
            return self.build_regime_not_found_payload(requested_regime), HTTPStatus.NOT_FOUND
        stacks = entry["stacks"]
        positions = entry["positions"]
        payload = {
            "ok": True,
            "runtimePrivatePackReadable": True,
            "fullRangeRenderEnabled": True,
            "stackCount": len(stacks),
            "minBb": min(stacks) if stacks else None,
            "maxBb": max(stacks) if stacks else None,
            "positionCount": len(positions),
        }
        payload.update(self.build_selected_regime_payload(entry))
        return payload, HTTPStatus.OK

    def stacks_payload(self, query: dict) -> tuple[dict, int]:
        requested_regime, entry = self.read_selected_regime(query)
        if not entry:
            return self.build_regime_not_found_payload(requested_regime), HTTPStatus.NOT_FOUND
        payload = {
            "ok": True,
            "runtimePrivatePackReadable": True,
            "fullRangeRenderEnabled": True,
            "stacks": entry["stacks"],
            "positions": entry["positions"],
            "secondaryPositionsByPosition": entry["secondaryPositionsByPosition"],
        }
        payload.update(self.build_selected_regime_payload(entry))
        return payload, HTTPStatus.OK

    def serve_stack_payload(self, query: dict) -> None:
        requested_regime, entry = self.read_selected_regime(query)
        if not entry:
            self.serve_json(self.build_regime_not_found_payload(requested_regime), HTTPStatus.NOT_FOUND)
            return
        bb_raw = (query.get("bb") or [""])[0]
        position = (query.get("position") or [""])[0]
        if not re.fullmatch(r"\d+", bb_raw):
            self.serve_json({"ok": False, "status": "invalid_bb"}, HTTPStatus.BAD_REQUEST)
            return
        bb = int(bb_raw)
        stack_map = entry["catalog"].get(bb)
        if not stack_map:
            self.serve_json(
                {"ok": False, "status": "stack_unavailable", "bb": bb, "selectedRegime": entry["id"]},
                HTTPStatus.NOT_FOUND,
            )
            return
        if position not in stack_map:
            self.serve_json(
                {
                    "ok": False,
                    "status": "position_unavailable",
                    "bb": bb,
                    "position": position,
                    "selectedRegime": entry["id"],
                },
                HTTPStatus.NOT_FOUND,
            )
            return
        secondary_position = (query.get("secondaryPosition") or [""])[0]
        range_payload = stack_map[position]
        if isinstance(range_payload, dict):
            if not secondary_position:
                self.serve_json(
                    {
                        "ok": False,
                        "status": "secondary_position_required",
                        "bb": bb,
                        "position": position,
                        "selectedRegime": entry["id"],
                    },
                    HTTPStatus.BAD_REQUEST,
                )
                return
            if secondary_position not in range_payload:
                self.serve_json(
                    {
                        "ok": False,
                        "status": "secondary_position_unavailable",
                        "bb": bb,
                        "position": position,
                        "secondaryPosition": secondary_position,
                        "selectedRegime": entry["id"],
                    },
                    HTTPStatus.NOT_FOUND,
                )
                return
            categories = range_payload[secondary_position]
        else:
            categories = range_payload
        unsafe_tuple_record = read_runtime_unsafe_tuple_record(
            self.app.get("runtimeSafety", {}),
            entry["id"],
            bb,
            position,
            secondary_position,
        )
        if unsafe_tuple_record:
            payload = {
                "ok": True,
                "status": "unsafe_tuple_non_authoritative",
                "bb": bb,
                "position": position,
                "categoryCount": 0,
                "categories": [],
                "bundleMembershipSafe": False,
                "nonAuthoritative": True,
                "exactSemanticsAuthority": unsafe_tuple_record.get("exactSemanticsAuthority", "normalized_pack"),
                "comparisonClass": unsafe_tuple_record.get("comparisonClass", "materially_lossy"),
                "lossModes": unsafe_tuple_record.get("lossModes", []),
                "lookupKeyTuple": unsafe_tuple_record.get("lookupKeyTuple", ""),
                "safetyGateNote": unsafe_tuple_record.get("note", ""),
                "secondaryPositionsByPosition": entry["secondaryPositionsByPosition"],
            }
            if secondary_position:
                payload["secondaryPosition"] = secondary_position
            payload.update(self.build_selected_regime_payload(entry))
            self.serve_json(payload)
            return
        payload = {
            "ok": True,
            "status": "ok",
            "bb": bb,
            "position": position,
            "categoryCount": len(categories),
            "categories": categories,
        }
        if secondary_position:
            payload["secondaryPosition"] = secondary_position
        payload.update(self.build_selected_regime_payload(entry))
        self.serve_json(payload)


def main() -> int:
    args = build_parser().parse_args()
    if args.export_public_bundle:
        bundle_payload = build_public_bundle_payload(args.pack, args.regimes_root)
        bundle_path = Path(args.export_public_bundle)
        write_json_file(bundle_path, bundle_payload)
        print(f"public_bundle_written {bundle_path}")
        return 0
    app_state = build_app_state(args.pack, args.regimes_root)
    runtime_safety = build_runtime_safety_state(args.safety_asset)
    mix_display_index = build_mix_display_state(args.mix_display_index)
    mix_ui_catalog, mix_ui_bundles = build_mix_ui_state(args.mix_ui_catalog)
    server = ThreadingHTTPServer((args.host, args.port), PrivatePackUiHandler)
    server.app = {  # type: ignore[attr-defined]
        "index": args.index,
        "runtimeSafety": runtime_safety,
        "mixDisplayIndex": mix_display_index,
        "mixUiCatalog": mix_ui_catalog,
        "mixUiBundles": mix_ui_bundles,
        **app_state,
    }
    print(f"private_pack_ui_server_ready {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
