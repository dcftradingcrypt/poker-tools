#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


RANKS = "AKQJT98765432"
RANK_INDEX = {rank: idx for idx, rank in enumerate(RANKS)}
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_PATH = REPO_ROOT / "out/_private/pushfold_real_data/pack.json"
DEFAULT_REGIMES_ROOT = REPO_ROOT / "out/_private/pushfold_real_data_regimes"
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
    parser.add_argument("--export-public-bundle", default="")
    return parser


@lru_cache(maxsize=None)
def load_pack(pack_path: str) -> dict:
    return json.loads(Path(pack_path).read_text(encoding="utf-8"))


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
    return {
        "stacks": stacks,
        "positions": positions,
        "secondaryPositionsByPosition": {
            str(position): [str(value) for value in values if isinstance(value, str)]
            for position, values in secondary_positions_by_position.items()
            if isinstance(values, list)
        },
        "catalog": catalog,
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
        self.send_error(HTTPStatus.NOT_FOUND)

    def serve_index(self) -> None:
        body = Path(self.app["index"]).read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
    server = ThreadingHTTPServer((args.host, args.port), PrivatePackUiHandler)
    server.app = {  # type: ignore[attr-defined]
        "index": args.index,
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
