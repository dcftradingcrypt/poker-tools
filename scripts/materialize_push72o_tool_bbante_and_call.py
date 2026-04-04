#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

import private_pack_ui_server as bundle_export


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = REPO_ROOT / "out/_private"
DEFAULT_REGIMES_ROOT = REPO_ROOT / "out/_private/pushfold_real_data_regimes"
DEFAULT_PUBLIC_BUNDLE_PATH = REPO_ROOT / "assets/pushfold/aof-bundle.v1.json"
SOURCE_PAGE_URL = "https://www.push72o.com/push-or-fold/"
SOURCE_JS_URL = "https://www.push72o.com/js/merged.js?v=2"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
POSITION_ORDER = ["UTG", "UTG+1", "UTG+2", "UTG+3", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
POSITION_ALIASES = {
    "UTG": "UTG",
    "UTG + 1": "UTG+1",
    "UTG + 2": "UTG+2",
    "UTG + 3": "UTG+3",
    "Lojack": "LJ",
    "Hijack": "HJ",
    "Cutoff": "CO",
    "Button": "BTN",
    "Small Blind": "SB",
    "Big Blind": "BB",
}
SOURCE_BUCKET_INDEX = 1
SOURCE_BUCKET_LABEL = "10% antes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    parser.add_argument("--regimes-root", default=str(DEFAULT_REGIMES_ROOT))
    parser.add_argument("--primary-pack", default=str(REPO_ROOT / "out/_private/pushfold_real_data/pack.json"))
    parser.add_argument("--public-bundle-path", default=str(DEFAULT_PUBLIC_BUNDLE_PATH))
    parser.add_argument("--timestamp")
    return parser


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-store"})
    with urlopen(request, timeout=30.0) as response:
        return response.read()


def normalize_position(raw_position: str) -> str:
    normalized = POSITION_ALIASES.get(raw_position.strip())
    if not normalized:
        raise RuntimeError(f"unsupported source position: {raw_position}")
    return normalized


def sort_positions(values: Iterable[str]) -> list[str]:
    unique = {value for value in values if value}
    return sorted(unique, key=lambda value: POSITION_ORDER.index(value))


def split_range_tokens(raw_value: str) -> list[str]:
    return [token.strip() for token in re.split(r"[\s,;]+", raw_value or "") if token.strip()]


def parse_shove_assignments(js_text: str) -> dict[int, dict[int, dict[str, str]]]:
    pattern = re.compile(r'shove_ranges\[(\d+)\]\["([^"]+)"\]\s*=\s*"([^"]*)"')
    parsed: dict[int, dict[int, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    for match in pattern.finditer(js_text):
        bucket_index = int(match.group(1))
        raw_key = match.group(2)
        raw_range = match.group(3).strip()
        key_match = re.fullmatch(r"(\d+)\s+BB\s+-\s+(.+)", raw_key)
        if not key_match:
            continue
        bb = int(key_match.group(1))
        position = normalize_position(key_match.group(2))
        parsed[bucket_index][bb][position] = raw_range
    return parsed


def parse_call_assignments(js_text: str) -> dict[int, dict[int, dict[str, dict[str, str]]]]:
    pattern = re.compile(
        r'call_range\[(\d+)\]\[(\d+)\]'
        r'(?:\["([^"]+)"\]|\.([A-Za-z]+))'
        r'(?:\["([^"]+)"\]|\.([A-Za-z]+))\s*=\s*"([^"]*)"'
    )
    parsed: dict[int, dict[int, dict[str, dict[str, str]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for match in pattern.finditer(js_text):
        bucket_index = int(match.group(1))
        bb = int(match.group(2))
        caller_raw = match.group(3) or match.group(4) or ""
        jammer_raw = match.group(5) or match.group(6) or ""
        raw_range = match.group(7).strip()
        caller = normalize_position(caller_raw)
        jammer = normalize_position(jammer_raw)
        parsed[bucket_index][bb][caller][jammer] = raw_range
    return parsed


def write_json(path: Path, payload: dict) -> str:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_text(text)


def write_shove_tsv(path: Path, stack_map: dict[int, dict[str, str]], positions: list[str]) -> str:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["bb", "position", "range"])
        for bb in sorted(stack_map):
            for position in positions:
                raw_range = stack_map[bb].get(position)
                if raw_range is None:
                    continue
                writer.writerow([bb, position, raw_range])
    return sha256_bytes(path.read_bytes())


def write_call_tsv(
    path: Path,
    stack_map: dict[str, dict[str, dict[str, str]]],
    jammer_positions: list[str],
    secondary_positions_by_jammer: dict[str, list[str]],
) -> str:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["bb", "position", "secondaryPosition", "range"])
        for bb_key in sorted(stack_map, key=lambda value: int(value)):
            for jammer in jammer_positions:
                caller_map = stack_map[bb_key].get(jammer, {})
                for caller in secondary_positions_by_jammer.get(jammer, []):
                    raw_range = caller_map.get(caller)
                    if raw_range is None:
                        continue
                    writer.writerow([bb_key, jammer, caller, raw_range])
    return sha256_bytes(path.read_bytes())


def build_shove_pack(stack_map: dict[int, dict[str, str]]) -> tuple[dict, list[str]]:
    positions = sort_positions(position for positions in stack_map.values() for position in positions)
    pack = {
        "meta": {
            "name": "push72o_tool_10max_bbante100_openjam",
            "table": "10max",
            "model": "push-fold",
            "maxPlayers": 10,
            "source": SOURCE_PAGE_URL,
            "license": "user to verify license",
            "notes": "private only / do not commit",
            "regimeId": "tool10max_bb100_openjam",
            "regimeLabel": "Tool 10max / BB ante 100% / Open jam",
            "sortIndex": 110,
            "assumptions": {
                "spot": "open-jam",
                "icm": "none",
                "model": "chipEV",
                "ante": "100% BB",
                "anteType": "big_blind",
                "anteSize": "100% BB",
                "sourceBucketIndex": str(SOURCE_BUCKET_INDEX),
                "sourceBucketAnte": SOURCE_BUCKET_LABEL,
                "rangeMode": "open_jam",
            },
        },
        "positions": positions,
        "stacksBb": sorted(stack_map),
        "ranges": {str(bb): stack_map[bb] for bb in sorted(stack_map)},
    }
    return pack, positions


def build_call_pack(stack_map: dict[int, dict[str, dict[str, str]]]) -> tuple[dict, list[str], dict[str, list[str]]]:
    jammer_positions = sort_positions(position for positions in stack_map.values() for position in positions)
    secondary_positions_by_jammer = {
        jammer: sort_positions(
            caller
            for caller_map in stack_map.values()
            for caller in caller_map.get(jammer, {}).keys()
        )
        for jammer in jammer_positions
    }
    pack = {
        "meta": {
            "name": "push72o_tool_10max_bbante100_call_vs_jam",
            "table": "10max",
            "model": "push-fold",
            "maxPlayers": 10,
            "source": SOURCE_PAGE_URL,
            "license": "user to verify license",
            "notes": "private only / do not commit",
            "regimeId": "tool10max_bb100_call",
            "regimeLabel": "Tool 10max / BB ante 100% / Call vs jam",
            "sortIndex": 111,
            "assumptions": {
                "spot": "call-vs-jam",
                "icm": "none",
                "model": "chipEV",
                "ante": "100% BB",
                "anteType": "big_blind",
                "anteSize": "100% BB",
                "sourceBucketIndex": str(SOURCE_BUCKET_INDEX),
                "sourceBucketAnte": SOURCE_BUCKET_LABEL,
                "rangeMode": "call_vs_jam",
                "primaryPositionRole": "jam_position",
                "secondaryPositionRole": "caller_position",
            },
        },
        "positions": jammer_positions,
        "secondaryPositionsByPosition": secondary_positions_by_jammer,
        "stacksBb": sorted(stack_map),
        "ranges": {str(bb): stack_map[bb] for bb in sorted(stack_map)},
    }
    return pack, jammer_positions, secondary_positions_by_jammer


def build_manifest(
    *,
    name: str,
    source_reference: str,
    generated_at: str,
    source_html_sha: str,
    source_js_sha: str,
    pack_sha: str,
    input_tsv_sha: str,
    assumptions: dict[str, str],
) -> dict:
    return {
        "manifestVersion": "1.0",
        "generatedAtUtc": generated_at,
        "packSha256": pack_sha,
        "inputTsvSha256": input_tsv_sha,
        "source": {
            "name": name,
            "reference": source_reference,
            "license": "user to verify license",
            "redistribution": "private only / do not commit",
        },
        "assumptions": assumptions,
        "notes": "Generated from private push-or-fold source.html and merged.js; acceptance artifacts only contain summaries.",
        "sourceUrl": source_reference,
        "sourceJsUrl": SOURCE_JS_URL,
        "retrievedAt": generated_at,
        "sourceHtmlSha256": source_html_sha,
        "sourceJsSha256": source_js_sha,
        "assumptionsNote": "Official Push72o push-or-fold tool / raw captures and staging packs stay under out/_private / BB ante 100% maps to source bucket 10% antes.",
    }


def main() -> int:
    args = build_parser().parse_args()
    out_root = Path(args.out_root)
    regimes_root = Path(args.regimes_root)
    primary_pack_path = Path(args.primary_pack)
    public_bundle_path = Path(args.public_bundle_path)
    timestamp = args.timestamp or default_timestamp()
    generated_at = utc_now_iso()

    source_run_dir = out_root / "pushfold_tool_source" / "_runs" / timestamp
    source_run_dir.mkdir(parents=True, exist_ok=True)

    html_body = fetch_bytes(SOURCE_PAGE_URL)
    js_body = fetch_bytes(SOURCE_JS_URL)
    source_html_path = source_run_dir / "source_push_or_fold.html"
    source_js_path = source_run_dir / "merged.js"
    source_html_path.write_bytes(html_body)
    source_js_path.write_bytes(js_body)
    source_html_sha = sha256_bytes(html_body)
    source_js_sha = sha256_bytes(js_body)
    js_text = js_body.decode("utf-8")

    shove_buckets = parse_shove_assignments(js_text)
    call_buckets = parse_call_assignments(js_text)
    if SOURCE_BUCKET_INDEX not in shove_buckets:
        raise RuntimeError(f"missing shove bucket {SOURCE_BUCKET_INDEX}")
    if SOURCE_BUCKET_INDEX not in call_buckets:
        raise RuntimeError(f"missing call bucket {SOURCE_BUCKET_INDEX}")

    shove_pack, shove_positions = build_shove_pack(shove_buckets[SOURCE_BUCKET_INDEX])
    call_stack_map: dict[int, dict[str, dict[str, str]]] = {}
    for bb, callers in call_buckets[SOURCE_BUCKET_INDEX].items():
        jammer_first: dict[str, dict[str, str]] = defaultdict(dict)
        for caller, caller_map in callers.items():
            for jammer, raw_range in caller_map.items():
                jammer_first[jammer][caller] = raw_range
        call_stack_map[bb] = {jammer: dict(caller_map) for jammer, caller_map in jammer_first.items()}
    call_pack, call_positions, secondary_positions_by_jammer = build_call_pack(call_stack_map)

    shove_dir = regimes_root / "tool10max_bb100_openjam"
    call_dir = regimes_root / "tool10max_bb100_call"
    shove_dir.mkdir(parents=True, exist_ok=True)
    call_dir.mkdir(parents=True, exist_ok=True)

    shove_pack_path = shove_dir / "pack.json"
    call_pack_path = call_dir / "pack.json"
    shove_pack_sha = write_json(shove_pack_path, shove_pack)
    call_pack_sha = write_json(call_pack_path, call_pack)

    shove_tsv_path = shove_dir / "input.tsv"
    call_tsv_path = call_dir / "input.tsv"
    shove_tsv_sha = write_shove_tsv(shove_tsv_path, shove_buckets[SOURCE_BUCKET_INDEX], shove_positions)
    call_tsv_sha = write_call_tsv(call_tsv_path, call_pack["ranges"], call_positions, secondary_positions_by_jammer)

    shove_manifest = build_manifest(
        name="push72o tool bb ante 100 open jam",
        source_reference=SOURCE_PAGE_URL,
        generated_at=generated_at,
        source_html_sha=source_html_sha,
        source_js_sha=source_js_sha,
        pack_sha=shove_pack_sha,
        input_tsv_sha=shove_tsv_sha,
        assumptions={
            "table": "10max",
            "spot": "open-jam",
            "icm": "none",
            "model": "chipEV",
            "ante": "100% BB",
            "anteType": "big_blind",
            "anteSize": "100% BB",
            "sourceBucketAnte": SOURCE_BUCKET_LABEL,
            "rangeMode": "open_jam",
        },
    )
    call_manifest = build_manifest(
        name="push72o tool bb ante 100 call vs jam",
        source_reference=SOURCE_PAGE_URL,
        generated_at=generated_at,
        source_html_sha=source_html_sha,
        source_js_sha=source_js_sha,
        pack_sha=call_pack_sha,
        input_tsv_sha=call_tsv_sha,
        assumptions={
            "table": "10max",
            "spot": "call-vs-jam",
            "icm": "none",
            "model": "chipEV",
            "ante": "100% BB",
            "anteType": "big_blind",
            "anteSize": "100% BB",
            "sourceBucketAnte": SOURCE_BUCKET_LABEL,
            "rangeMode": "call_vs_jam",
            "primaryPositionRole": "jam_position",
            "secondaryPositionRole": "caller_position",
        },
    )
    write_json(shove_dir / "manifest.json", shove_manifest)
    write_json(call_dir / "manifest.json", call_manifest)

    public_bundle = bundle_export.build_public_bundle_payload(str(primary_pack_path), str(regimes_root))
    bundle_export.write_json_file(public_bundle_path, public_bundle)

    sample = {
        "openJamSample": shove_buckets[SOURCE_BUCKET_INDEX].get(11, {}).get("UTG+2", ""),
        "callSample": call_pack["ranges"].get("11", {}).get("UTG+2", {}).get("UTG+1", ""),
    }
    print(json.dumps(
        {
            "status": "ok",
            "sourceHtml": str(source_html_path),
            "sourceJs": str(source_js_path),
            "shovePack": str(shove_pack_path),
            "callPack": str(call_pack_path),
            "publicBundle": str(public_bundle_path),
            "sample": sample,
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
