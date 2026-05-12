#!/usr/bin/env python3
"""Content-source checks for the mix-game hand range surfaces.

This verifier is intentionally about content, not only runtime wiring. It
checks that visible range numbers and boundary claims in index.html are backed
by the repo's source notes/assets, and that 826 does not present public-source
archetypes as an exact positional range matrix.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONTENT_CHECK_VERSION = "1.4"
PUBLIC_COPY_PATHS = [
    "index.html",
    "assets/mix/badugi-pre-draw-public-ranges.v1.json",
    "assets/mix/a5-triple-draw-public-ranges.v1.json",
    "assets/mix/stud8-third-street-public-ranges.v1.json",
    "assets/mix/basil-826-public-ranges.v1.json",
    "assets/mix/badugi-pre-draw-public-ranges.embedded.v1.js",
    "assets/mix/a5-triple-draw-public-ranges.embedded.v1.js",
    "assets/mix/stud8-third-street-public-ranges.embedded.v1.js",
    "assets/mix/basil-826-public-ranges.embedded.v1.js",
]


@dataclass
class CheckResult:
    check_id: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "checkId": self.check_id,
            "status": self.status,
            "detail": self.detail,
        }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def add_check(checks: list[CheckResult], check_id: str, ok: bool, detail: str) -> None:
    checks.append(CheckResult(check_id, "passed" if ok else "failed", detail))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def find_js_assignment_literal(source: str, name: str) -> str:
    needle = f"const {name} = "
    start = source.find(needle)
    if start < 0:
        raise ValueError(f"missing JS const {name}")
    cursor = start + len(needle)
    while cursor < len(source) and source[cursor].isspace():
        cursor += 1
    if cursor >= len(source) or source[cursor] not in "{[":
        raise ValueError(f"JS const {name} is not an object/array literal")
    opener = source[cursor]
    closer = "}" if opener == "{" else "]"
    depth = 0
    quote = ""
    escaped = False
    for index in range(cursor, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return source[cursor : index + 1]
    raise ValueError(f"unterminated JS const {name}")


def extract_index_literals(index_html: str, names: list[str]) -> dict[str, Any]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found")
    assignments = []
    for name in names:
        literal = find_js_assignment_literal(index_html, name)
        assignments.append(f"const {name} = {literal};")
    assignments.append(f"console.log(JSON.stringify({{{', '.join(names)}}}));")
    script = "\n".join(assignments)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(script)
    try:
        completed = subprocess.run(
            [node, str(temp_path)],
            check=False,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
    if completed.returncode != 0:
        raise RuntimeError(f"node literal extraction failed: {completed.stderr[:500]}")
    return json.loads(completed.stdout)


def normalize_text(value: Any) -> str:
    return " ".join(str(value).replace("+", " plus ").replace("/", " ").replace(",", " ").split()).lower()


def contains_all(haystack: Any, needles: list[str]) -> bool:
    normalized = normalize_text(haystack)
    return all(normalize_text(needle) in normalized for needle in needles)


def iter_source_refs(payload: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(payload, dict):
        source_ref = payload.get("source_ref")
        if isinstance(source_ref, str) and source_ref:
            refs.append(source_ref)
        source_refs = payload.get("source_refs")
        if isinstance(source_refs, list):
            refs.extend(str(ref) for ref in source_refs if isinstance(ref, str) and ref)
        for value in payload.values():
            refs.extend(iter_source_refs(value))
    elif isinstance(payload, list):
        for value in payload:
            refs.extend(iter_source_refs(value))
    return refs


def verify_public_asset_lineage(checks: list[CheckResult], root: Path, rel_path: str) -> None:
    payload = read_json(root / rel_path)
    source_index = payload.get("source_index") if isinstance(payload, dict) else {}
    source_extracts = payload.get("source_extracts") if isinstance(payload, dict) else {}
    refs = sorted(set(iter_source_refs(payload)))
    add_check(
        checks,
        f"asset.{Path(rel_path).stem}.has_source_index",
        isinstance(source_index, dict) and bool(source_index),
        f"{rel_path} source_index entries={len(source_index) if isinstance(source_index, dict) else 0}",
    )
    add_check(
        checks,
        f"asset.{Path(rel_path).stem}.has_source_extracts",
        isinstance(source_extracts, dict) and bool(source_extracts),
        f"{rel_path} source_extracts entries={len(source_extracts) if isinstance(source_extracts, dict) else 0}",
    )
    add_check(
        checks,
        f"asset.{Path(rel_path).stem}.has_source_refs",
        bool(refs),
        f"{rel_path} source refs checked={len(refs)}",
    )
    missing = [
        ref
        for ref in refs
        if not (isinstance(source_index, dict) and ref in source_index)
        or not (isinstance(source_extracts, dict) and ref in source_extracts)
    ]
    add_check(
        checks,
        f"asset.{Path(rel_path).stem}.source_refs_resolve",
        not missing,
        f"{rel_path} source refs checked={len(refs)} missing={missing[:20]}",
    )


def verify_badugi(checks: list[CheckResult], literals: dict[str, Any], badugi: dict[str, Any]) -> None:
    sections = literals["MIX_GAME_RANGE_SECTIONS"]["badugi"]
    opening_rows = sections[0]["rows"]
    extracts = badugi["source_extracts"]["countingouts_p3"]["position_notes"]
    expected = {
        "EP": ["14.3%", "J-high", "breakable Q/K", "75X"],
        "MP": ["18.2%", "Q-high", "breakable K", "A48"],
        "CO": ["28.3%", "all badugis", "8", "A2", "A3"],
        "BTN": ["38.2%", "all badugis", "9", "A2", "A3", "23", "A4"],
        "SB": ["BTN baseline", "24", "34", "A5", "25", "35", "45"],
    }
    errors = []
    for position, pct, row_text in opening_rows:
        note = extracts.get(position, "")
        if position in expected and not contains_all(f"{pct} {row_text} {note}", expected[position]):
            errors.append(f"{position}:{pct}:{row_text}")
    add_check(
        checks,
        "content.badugi.opening_thresholds_match_source_extracts",
        not errors and len(opening_rows) == 5,
        f"checked {len(opening_rows)} Badugi opening rows; errors={errors}",
    )


def verify_a5(checks: list[CheckResult], literals: dict[str, Any], a5: dict[str, Any]) -> None:
    sections = literals["MIX_GAME_RANGE_SECTIONS"]["a5_triple_draw"]
    opening_rows = sections[0]["rows"]
    extracts = a5["source_extracts"]["countingouts_predraw"]["position_notes"]
    expected = {
        "EP/HJ": ["26.7%", "Made 7s", "Four Wheel", "Four to a Six", "Three Wheel", "A26-A46", "236", "246", "346"],
        "CO": ["31.7%", "Three to a Six"],
        "BTN": ["42.7%", "A2 through 34"],
        "SB": ["button range", "tough"],
        "BB": ["button range", "late", "SB"],
    }
    source_by_row = {
        "EP/HJ": extracts.get("EP", ""),
        "CO": extracts.get("CO", ""),
        "BTN": extracts.get("BTN", ""),
        "SB": extracts.get("SB", ""),
        "BB": extracts.get("BB", ""),
    }
    errors = []
    for position, pct, row_text in opening_rows:
        if position in expected and not contains_all(f"{pct} {row_text} {source_by_row.get(position, '')}", expected[position]):
            errors.append(f"{position}:{pct}:{row_text}")
    add_check(
        checks,
        "content.a5.opening_thresholds_match_source_extracts",
        not errors and len(opening_rows) == 5,
        f"checked {len(opening_rows)} A-5 opening rows; errors={errors}",
    )


def verify_plans(checks: list[CheckResult], literals: dict[str, Any], root: Path) -> None:
    sections = literals["MIX_GAME_RANGE_SECTIONS"]
    plo_plan = read_text(root / "out/_codex/plo_high_rank_bucket_and_ui_plan.md")
    o8_plan = read_text(root / "out/_codex/o8_rank_bucket_and_ui_plan.md")
    deuce_plan = read_text(root / "out/_codex/deuce_to_seven_triple_draw_rank_bucket_and_ui_plan.md")

    plo_rows = sections["plo_high"][0]["rows"]
    plo_errors = [row for row in plo_rows if row[1] not in plo_plan or row[0] not in plo_plan]
    add_check(
        checks,
        "content.plo.position_totals_match_plan",
        not plo_errors and len(plo_rows) == 5,
        f"PLO totals checked={len(plo_rows)} errors={plo_errors}",
    )

    o8_rows = sections["o8"][0]["rows"]
    o8_errors = [row for row in o8_rows if not all(str(value) in o8_plan for value in row)]
    add_check(
        checks,
        "content.o8.whole_chart_summary_matches_plan",
        not o8_errors and len(o8_rows) == 4,
        f"O8 summary rows checked={len(o8_rows)} errors={o8_errors}",
    )

    deuce_compact_rows = sections["deuce_to_seven_triple_draw"][0]["rows"]
    deuce_detailed_rows = sections["deuce_to_seven_triple_draw"][1]["rows"]
    deuce_errors = [
        row
        for row in deuce_compact_rows + deuce_detailed_rows
        if not all(str(value).split()[0] in deuce_plan for value in row[:2])
    ]
    add_check(
        checks,
        "content.deuce_to_seven.threshold_profiles_match_plan",
        not deuce_errors and len(deuce_compact_rows) == 4 and len(deuce_detailed_rows) == 4,
        f"2-7 rows checked={len(deuce_compact_rows) + len(deuce_detailed_rows)} errors={deuce_errors}",
    )


def verify_826(checks: list[CheckResult], literals: dict[str, Any], root: Path, index_html: str) -> None:
    asset = read_json(root / "assets/mix/basil-826-public-ranges.v1.json")
    surfaces = {entry["gameId"]: entry for entry in literals["MIX_GAME_SURFACES"]}
    surface = surfaces.get("basil_826", {})
    ranges = asset.get("hand_ranges", {})
    source_index = asset.get("source_index", {})
    source_coverage = asset.get("source_coverage", [])
    forbidden_position_keys = {"UTG", "HJ", "CO", "BTN", "SB"}
    forbidden_view_keys = {"open_raise", "bb_defense_call"}
    found_position_keys = []
    found_view_keys = []
    non_source_confirmed_keys = []
    empty_entries = []
    actual_views = []
    for variant, variant_payload in ranges.items():
        if not isinstance(variant_payload, dict):
            continue
        found_view_keys.extend(sorted(forbidden_view_keys.intersection(variant_payload)))
        for view, view_payload in variant_payload.items():
            actual_views.append(f"{variant}.{view}")
            if isinstance(view_payload, dict):
                found_position_keys.extend(sorted(forbidden_position_keys.intersection(view_payload)))
                position_keys = sorted(view_payload)
                if position_keys != ["SOURCE_CONFIRMED"]:
                    non_source_confirmed_keys.append(f"{variant}.{view}:{position_keys}")
                rows = view_payload.get("SOURCE_CONFIRMED")
                if not isinstance(rows, list) or not rows:
                    empty_entries.append(f"{variant}.{view}")
    scope = asset.get("scope", {})
    add_check(
        checks,
        "content.826.no_public_positional_matrix_claim",
        not found_position_keys
        and not found_view_keys
        and not non_source_confirmed_keys
        and not empty_entries
        and scope.get("position_model") == "not_available_from_public_sources"
        and surface.get("coverageTier") == "source_confirmed_archetypes",
        (
            f"826 forbidden position keys={found_position_keys}; forbidden view keys={found_view_keys}; "
            f"non_source_confirmed_keys={non_source_confirmed_keys}; empty_entries={empty_entries}; "
            f"coverageTier={surface.get('coverageTier')}"
        ),
    )
    coverage_refs = sorted(
        {
            entry.get("source_ref")
            for entry in source_coverage
            if isinstance(entry, dict) and isinstance(entry.get("source_ref"), str)
        }
    )
    covered_views = sorted(
        {
            view
            for entry in source_coverage
            if isinstance(entry, dict)
            for view in entry.get("views", [])
            if isinstance(view, str)
        }
    )
    missing_source_refs = sorted(set(source_index) - set(coverage_refs)) if isinstance(source_index, dict) else []
    missing_views = sorted(set(actual_views) - set(covered_views))
    extra_views = sorted(set(covered_views) - set(actual_views) - {"scope_boundary"})
    empty_coverage_entries = [
        str(index)
        for index, entry in enumerate(source_coverage)
        if not isinstance(entry, dict)
        or not isinstance(entry.get("source_ref"), str)
        or not entry.get("source_ref")
        or not isinstance(entry.get("views"), list)
        or not entry.get("views")
    ]
    add_check(
        checks,
        "content.826.source_coverage_complete",
        isinstance(source_coverage, list)
        and bool(source_coverage)
        and not missing_source_refs
        and not missing_views
        and not extra_views
        and not empty_coverage_entries
        and "scope_boundary" in covered_views,
        (
            f"826 source refs={coverage_refs}; missing_source_refs={missing_source_refs}; "
            f"missing_views={missing_views}; extra_views={extra_views}; "
            f"empty_coverage_entries={empty_coverage_entries}"
        ),
    )
    add_check(
        checks,
        "content.826.ui_boundary_text_present",
        "position 別の open range や BB defense matrix は、現時点の資料からは確定できません" in index_html
        and "exact public frequency chart はないため" in index_html,
        "826 UI must tell users that exact positional ranges are not confirmed",
    )


def verify_japanese_copy(checks: list[CheckResult], index_html: str) -> None:
    mix_start = index_html.find("const MIX_DISPLAY_CLASS_META")
    mix_end = index_html.find("const MIX_GAME_RANGE_SECTIONS")
    mix_copy = index_html[mix_start:mix_end] if mix_start >= 0 and mix_end > mix_start else index_html
    banned = [
        "pretending",
        "honest に",
        "widen する",
        "widen できる",
        "still need fallback equity",
        "hand range だけ",
        "confidence, source links",
    ]
    found = [needle for needle in banned if needle in mix_copy]
    add_check(
        checks,
        "copy.mix_meta.no_obvious_broken_japanese",
        not found,
        f"banned awkward fragments found={found}",
    )


def verify_public_copy_files(checks: list[CheckResult], root: Path) -> None:
    banned_fragments = [
        "pretending",
        "honest に",
        "widen する",
        "widen できる",
        "still need fallback equity",
        "hand range だけ",
        "confidence, source links",
    ]
    mojibake_signatures = [
        "縺",
        "繧",
        "譁",
        "螟",
        "荳",
        "隱",
        "逕",
        "驛",
        "髱",
    ]
    fragment_hits: dict[str, list[str]] = {}
    mojibake_hits: dict[str, list[str]] = {}
    for rel_path in PUBLIC_COPY_PATHS:
        text = read_text(root / rel_path)
        fragments = [needle for needle in banned_fragments if needle in text]
        mojibake = [needle for needle in mojibake_signatures if needle in text]
        if fragments:
            fragment_hits[rel_path] = fragments
        if mojibake:
            mojibake_hits[rel_path] = mojibake
    add_check(
        checks,
        "copy.public_surfaces.no_obvious_broken_fragments",
        not fragment_hits,
        f"broken fragment hits={fragment_hits}",
    )
    add_check(
        checks,
        "copy.public_surfaces.no_mojibake_signatures",
        not mojibake_hits,
        f"mojibake signature hits={mojibake_hits}",
    )


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    checks: list[CheckResult] = []
    index_html = read_text(root / "index.html")
    try:
        literals = extract_index_literals(
            index_html,
            [
                "MIX_COVERAGE_TIER_META",
                "MIX_GAME_SURFACES",
                "MIX_GAME_UI_META",
                "MIX_GAME_RANGE_SECTIONS",
            ],
        )
        add_check(checks, "input.index_js_literals.extract", True, "mix JS literals extracted with node")
    except Exception as exc:
        literals = {}
        add_check(checks, "input.index_js_literals.extract", False, f"failed to extract mix JS literals: {exc}")

    for rel_path in [
        "assets/mix/badugi-pre-draw-public-ranges.v1.json",
        "assets/mix/a5-triple-draw-public-ranges.v1.json",
        "assets/mix/stud8-third-street-public-ranges.v1.json",
        "assets/mix/basil-826-public-ranges.v1.json",
    ]:
        try:
            verify_public_asset_lineage(checks, root, rel_path)
        except Exception as exc:
            add_check(checks, f"asset.{Path(rel_path).stem}.lineage_exception", False, str(exc))

    if literals:
        try:
            verify_badugi(checks, literals, read_json(root / "assets/mix/badugi-pre-draw-public-ranges.v1.json"))
        except Exception as exc:
            add_check(checks, "content.badugi.exception", False, str(exc))
        try:
            verify_a5(checks, literals, read_json(root / "assets/mix/a5-triple-draw-public-ranges.v1.json"))
        except Exception as exc:
            add_check(checks, "content.a5.exception", False, str(exc))
        try:
            verify_plans(checks, literals, root)
        except Exception as exc:
            add_check(checks, "content.plans.exception", False, str(exc))
        try:
            verify_826(checks, literals, root, index_html)
        except Exception as exc:
            add_check(checks, "content.826.exception", False, str(exc))
    verify_japanese_copy(checks, index_html)
    verify_public_copy_files(checks, root)

    failed = [check for check in checks if check.status != "passed"]
    return {
        "status": "passed" if not failed else "failed",
        "contentCheckVersion": CONTENT_CHECK_VERSION,
        "repoRoot": str(root),
        "checks": [check.as_dict() for check in checks] if args.verbose or failed else [],
        "summary": {
            "checksTotal": len(checks),
            "checksPassed": len(checks) - len(failed),
            "checksFailed": len(failed),
            "failedCheckIds": [check.check_id for check in failed],
        },
        "residualRisk": [
            "This verifier checks repo-local source alignment and boundary language; it does not prove poker EV optimality.",
            "Public web pages can change after the repo-local source notes were captured.",
            "826 remains source-confirmed archetype guidance, not an exact positional chart.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="include passed checks in JSON output")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = build_payload(args)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
