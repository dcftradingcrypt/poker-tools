#!/usr/bin/env python3
"""Verify the current mix-game grounding/display strategy boundary.

This is the current-strategy companion to the older blocked-family intake
regressions. It proves the repo is separating:

- exact retained source slices,
- grounded practical heuristic coverage,
- visible public-source surfaces that are not normalized structural-family
  bundles, and
- the AoF push/fold lane that is intentionally outside the mix display matrix.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STRATEGY_CHECK_VERSION = "1.0"

ALL_STRUCTURAL_FAMILIES = [
    "cc_high / 2-card",
    "cc_high / 4-card",
    "cc_hilo / 4-card",
    "stud_high",
    "stud_low_razz",
    "stud_hilo",
    "draw_triple_low",
]
MIX_DISPLAY_FAMILIES = [
    "cc_high / 4-card",
    "cc_hilo / 4-card",
    "stud_high",
    "stud_low_razz",
    "stud_hilo",
    "draw_triple_low",
]
EXACT_DISPLAY_FAMILIES = {
    "cc_high / 4-card",
    "cc_hilo / 4-card",
}
PRACTICAL_DISPLAY_FAMILIES = {
    "stud_high",
    "stud_low_razz",
    "stud_hilo",
    "draw_triple_low",
}
EXPECTED_CATALOG_CLASSES = {
    "cc_high / 4-card": ("grounded_exact_display", "tool_ready_exact_preflop_slice"),
    "cc_hilo / 4-card": ("grounded_exact_display", "tool_ready_exact_preflop_slice"),
    "stud_high": ("grounded_practical_coverage", "reference_only"),
    "stud_low_razz": ("grounded_practical_coverage", "reference_only"),
    "stud_hilo": ("grounded_practical_coverage", "reference_only"),
    "draw_triple_low": ("grounded_practical_coverage", "reference_only"),
}
EXPECTED_VISIBLE_GAME_IDS = [
    "plo_high",
    "o8",
    "plo8",
    "badugi",
    "a5_triple_draw",
    "deuce_to_seven_triple_draw",
    "razz",
    "stud_high",
    "stud8",
    "basil_826",
]
PUBLIC_SOURCE_ASSETS = {
    "badugi": "assets/mix/badugi-pre-draw-public-ranges.v1.json",
    "a5_triple_draw": "assets/mix/a5-triple-draw-public-ranges.v1.json",
    "stud8": "assets/mix/stud8-third-street-public-ranges.v1.json",
    "basil_826": "assets/mix/basil-826-public-ranges.v1.json",
}
EXPECTED_FILES = {
    "registry": "out/_codex/mix_game_family_contract_registry.json",
    "grounding_gates": "out/_codex/mix_game_grounding_gates.md",
    "coverage_matrix": "out/_codex/poker_mix_family_coverage_matrix.md",
    "catalog": "out/_codex/poker_mix_ui_catalog.json",
    "display_index": "out/_codex/poker_mix_display_index.json",
    "synthesis_contract": "out/_codex/mix_cross_game_ui_synthesis_contract.json",
    "index_html": "index.html",
    "pushfold_bundle": "assets/pushfold/aof-bundle.v1.json",
    "pushfold_safety": "assets/pushfold/aof-bundle-safety.v1.json",
    "handoff": "HANDOFF_PACKET.md",
    "bootstrap": "NEW_CHAT_BOOTSTRAP.md",
    "blocked_healthcheck": "scripts/verify_mix_game_blocked_family_toolchain_health.py",
}


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


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value is not an object")
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def by_key(items: Any, key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list):
        return result
    for item in items:
        if isinstance(item, dict) and isinstance(item.get(key), str):
            result[item[key]] = item
    return result


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def normalize_optional_path(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def add_check(checks: list[CheckResult], check_id: str, ok: bool, detail: str) -> None:
    checks.append(CheckResult(check_id, "passed" if ok else "failed", detail))


def path_exists(root: Path, rel_path: str) -> bool:
    return bool(rel_path) and (root / rel_path).is_file()


def json_path_exists(root: Path, rel_path: str) -> bool:
    if not path_exists(root, rel_path):
        return False
    read_json_object(root / rel_path)
    return True


def extract_js_string(body: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*:\s*'([^']*)'", body)
    return match.group(1) if match else ""


def extract_js_string_array(body: str, name: str) -> list[str]:
    match = re.search(rf"\b{name}\s*:\s*\[([^\]]*)\]", body, re.S)
    if not match:
        return []
    return re.findall(r"'([^']*)'", match.group(1))


def extract_mix_game_surfaces(index_html: str) -> list[dict[str, Any]]:
    block_match = re.search(r"const\s+MIX_GAME_SURFACES\s*=\s*\[(.*?)\];", index_html, re.S)
    if not block_match:
        return []
    block = block_match.group(1)
    surfaces: list[dict[str, Any]] = []
    for object_match in re.finditer(r"\{(.*?)\}", block, re.S):
        body = object_match.group(1)
        game_id = extract_js_string(body, "gameId")
        if not game_id:
            continue
        surfaces.append(
            {
                "gameId": game_id,
                "familyId": extract_js_string(body, "familyId"),
                "displayClass": extract_js_string(body, "displayClass"),
                "coverageTier": extract_js_string(body, "coverageTier"),
                "repoArtifact": extract_js_string(body, "repoArtifact"),
                "planningDoc": extract_js_string(body, "planningDoc"),
                "selectorAxes": extract_js_string_array(body, "selectorAxes"),
            }
        )
    return surfaces


def extract_embedded_scripts(index_html: str) -> list[str]:
    return re.findall(r'<script\s+src="([^"]+\.embedded\.v1\.js)"', index_html)


def compare_sets(
    checks: list[CheckResult], check_id: str, observed: list[str], expected: list[str], detail_label: str
) -> None:
    observed_set = set(observed)
    expected_set = set(expected)
    missing = sorted(expected_set - observed_set)
    extra = sorted(observed_set - expected_set)
    add_check(
        checks,
        check_id,
        not missing and not extra,
        f"{detail_label}; observed={sorted(observed_set)} missing={missing} extra={extra}",
    )


def verify_registry(checks: list[CheckResult], registry: dict[str, Any]) -> None:
    boundary = registry.get("currentGroundingBoundary")
    boundary = boundary if isinstance(boundary, dict) else {}
    compare_sets(
        checks,
        "registry.grounded_structural_families",
        string_list(boundary.get("groundedFamilies")),
        ALL_STRUCTURAL_FAMILIES,
        "current registry boundary must ground exactly the seven structural families",
    )
    compare_sets(
        checks,
        "registry.blocked_families_empty",
        string_list(boundary.get("blockedFamilies")),
        [],
        "current registry boundary must have no blocked families",
    )
    registry_families = by_key(registry.get("families"), "familyId")
    compare_sets(
        checks,
        "registry.mix_family_entries",
        list(registry_families),
        MIX_DISPLAY_FAMILIES,
        "registry family entries must match the six mix-display families; cc_high / 2-card stays push/fold-only",
    )
    not_grounded = [
        family_id
        for family_id in MIX_DISPLAY_FAMILIES
        if registry_families.get(family_id, {}).get("currentRepoStatus") != "grounded"
    ]
    add_check(
        checks,
        "registry.mix_family_statuses",
        not not_grounded,
        f"all six mix-display registry entries must be grounded; not_grounded={not_grounded}",
    )


def verify_catalog_and_display_index(
    checks: list[CheckResult],
    root: Path,
    catalog: dict[str, Any],
    display_index: dict[str, Any],
) -> None:
    catalog_families = by_key(catalog.get("families"), "familyId")
    index_families = by_key(display_index.get("families"), "familyId")
    compare_sets(
        checks,
        "catalog.family_set",
        list(catalog_families),
        MIX_DISPLAY_FAMILIES,
        "catalog must expose the six non-AoF mix families",
    )
    compare_sets(
        checks,
        "display_index.family_set",
        list(index_families),
        MIX_DISPLAY_FAMILIES,
        "display index must expose the same six non-AoF mix families",
    )
    add_check(
        checks,
        "catalog.aof_exclusion_note",
        "cc_high / 2-card" in str(catalog.get("note", "")) and "intentionally excluded" in str(catalog.get("note", "")),
        "catalog must explicitly state that AoF cc_high / 2-card is intentionally excluded",
    )
    index_boundary = display_index.get("currentBoundary")
    index_boundary = index_boundary if isinstance(index_boundary, dict) else {}
    compare_sets(
        checks,
        "display_index.current_boundary",
        string_list(index_boundary.get("groundedFamilies")),
        MIX_DISPLAY_FAMILIES,
        "display index boundary must include exactly the six visible mix families",
    )
    compare_sets(
        checks,
        "display_index.blocked_empty",
        string_list(index_boundary.get("blockedFamilies")),
        [],
        "display index boundary must not carry blocked families",
    )

    for family_id in MIX_DISPLAY_FAMILIES:
        expected_display_class, expected_tool_status = EXPECTED_CATALOG_CLASSES[family_id]
        catalog_entry = catalog_families.get(family_id, {})
        index_entry = index_families.get(family_id, {})
        bundle_path = normalize_optional_path(catalog_entry.get("bundleArtifact"))
        source_pack_path = normalize_optional_path(catalog_entry.get("sourcePackPath"))
        detail_path = normalize_optional_path(catalog_entry.get("detailArtifact"))
        bundle: dict[str, Any] = {}
        bundle_loaded = False
        try:
            if bundle_path:
                bundle = read_json_object(root / bundle_path)
                bundle_loaded = True
        except (OSError, json.JSONDecodeError, ValueError):
            bundle_loaded = False

        add_check(
            checks,
            f"catalog.{family_id}.classification",
            catalog_entry.get("displayClass") == expected_display_class
            and catalog_entry.get("toolStatus") == expected_tool_status
            and index_entry.get("displayClass") == expected_display_class,
            (
                f"{family_id} must keep expected display/tool class "
                f"{expected_display_class}/{expected_tool_status}"
            ),
        )
        add_check(
            checks,
            f"catalog.{family_id}.artifacts_exist",
            path_exists(root, bundle_path)
            and path_exists(root, source_pack_path)
            and path_exists(root, str(Path(source_pack_path).with_name("manifest.json")))
            and path_exists(root, detail_path),
            (
                f"{family_id} must have bundle, source pack, manifest, and detail artifact; "
                f"bundle={bundle_path} sourcePack={source_pack_path} detail={detail_path}"
            ),
        )
        expected_spot_count = catalog_entry.get("spotCount")
        actual_spots = bundle.get("spots") if isinstance(bundle, dict) else None
        add_check(
            checks,
            f"catalog.{family_id}.bundle_shape",
            bundle_loaded
            and bundle.get("familyId") == family_id
            and bundle.get("displayClass") == expected_display_class
            and bundle.get("spotCount") == expected_spot_count
            and isinstance(actual_spots, list)
            and len(actual_spots) == expected_spot_count
            and isinstance(expected_spot_count, int)
            and expected_spot_count > 0,
            f"{family_id} bundle must be valid JSON with matching family/display/spot count",
        )
        if family_id in EXACT_DISPLAY_FAMILIES:
            add_check(
                checks,
                f"display_index.{family_id}.exact_scope",
                index_entry.get("sourceClass") in {"retained_exact_commit_archive", "retained_exact_commit_chart_html"}
                and "tool-ready exact" in str(index_entry.get("repoReadyScope", "")),
                f"{family_id} must be labeled as a narrow exact retained-source slice",
            )
        if family_id in PRACTICAL_DISPLAY_FAMILIES:
            add_check(
                checks,
                f"display_index.{family_id}.practical_scope",
                index_entry.get("sourceClass") == "retained_strategy_article"
                and "reference-only practical coverage" in str(index_entry.get("repoReadyScope", "")),
                f"{family_id} must be labeled as reference-only practical heuristic coverage",
            )
        staged_artifacts = string_list(index_entry.get("stagedArtifacts"))
        add_check(
            checks,
            f"display_index.{family_id}.staged_artifacts_exist",
            bool(staged_artifacts) and all(path_exists(root, path) for path in staged_artifacts),
            f"{family_id} display index staged artifacts must exist",
        )


def verify_markdown_claim_boundaries(
    checks: list[CheckResult], grounding_gates_text: str, coverage_matrix_text: str
) -> None:
    add_check(
        checks,
        "docs.practical_not_exact_claims",
        grounding_gates_text.count("article-derived practical coverage, not an exact chart") >= 4
        and "grounded practical coverage" in coverage_matrix_text
        and "article-derived practical heuristic coverage" in coverage_matrix_text,
        "stud/draw practical families must be explicitly bounded away from exact chart claims",
    )
    add_check(
        checks,
        "docs.exact_slice_limits",
        "preflop push/fold focused" in grounding_gates_text
        and "accepted representative `HU-100bb-with-limp` source slice" in grounding_gates_text
        and "accepted opening-chart slice, not a full family corpus" in grounding_gates_text,
        "exact families must preserve narrow-scope limits for AoF, PLO, and O8",
    )
    add_check(
        checks,
        "docs.aof_mix_lane_separation",
        "intentionally excluded from this matrix" in coverage_matrix_text
        and "Push/Fold lane" in coverage_matrix_text,
        "coverage matrix must keep cc_high / 2-card outside the mix display lane",
    )


def verify_pushfold_lane(checks: list[CheckResult], root: Path) -> None:
    bundle_path = root / EXPECTED_FILES["pushfold_bundle"]
    safety_path = root / EXPECTED_FILES["pushfold_safety"]
    try:
        bundle = read_json_object(bundle_path)
        safety = read_json_object(safety_path)
        bundle_ok = isinstance(bundle.get("regimes"), dict) and bool(bundle.get("regimes"))
        safety_ok = (
            safety.get("familyIdOrLabel") == "cc_high / 2-card"
            and safety.get("defaultBundleMembershipSafe") is True
        )
    except (OSError, json.JSONDecodeError, ValueError):
        bundle_ok = False
        safety_ok = False
    add_check(
        checks,
        "pushfold.aof_bundle_and_safety",
        bundle_ok and safety_ok,
        "cc_high / 2-card must stay grounded through the push/fold bundle plus safety manifest",
    )


def verify_contract_and_html(checks: list[CheckResult], root: Path, contract: dict[str, Any], index_html: str) -> None:
    html_surfaces = by_key(extract_mix_game_surfaces(index_html), "gameId")
    contract_games = by_key(contract.get("games"), "gameId")
    compare_sets(
        checks,
        "html.visible_game_surfaces",
        list(html_surfaces),
        EXPECTED_VISIBLE_GAME_IDS,
        "index.html must expose the expected visible mix game surfaces",
    )
    compare_sets(
        checks,
        "contract.visible_game_surfaces",
        list(contract_games),
        EXPECTED_VISIBLE_GAME_IDS,
        "synthesis contract must cover the same visible game surfaces as index.html",
    )

    tier_ids = {entry.get("id") for entry in contract.get("coverageTiers", []) if isinstance(entry, dict)}
    display_classes = by_key(contract.get("displayClasses"), "id")
    for game_id in EXPECTED_VISIBLE_GAME_IDS:
        html_surface = html_surfaces.get(game_id, {})
        contract_game = contract_games.get(game_id, {})
        html_artifact = normalize_optional_path(html_surface.get("repoArtifact"))
        contract_artifact = normalize_optional_path(contract_game.get("repoArtifact"))
        html_planning = normalize_optional_path(html_surface.get("planningDoc"))
        contract_planning = normalize_optional_path(contract_game.get("planningDoc"))
        display_class = normalize_optional_path(contract_game.get("displayClass"))
        used_by = string_list(display_classes.get(display_class, {}).get("usedBy"))
        artifact_ok = html_artifact == contract_artifact and (not contract_artifact or path_exists(root, contract_artifact))
        planning_ok = html_planning == contract_planning and (not contract_planning or path_exists(root, contract_planning))
        add_check(
            checks,
            f"contract.{game_id}.matches_html",
            contract_game.get("displayClass") == html_surface.get("displayClass")
            and contract_game.get("coverageTier") == html_surface.get("coverageTier")
            and string_list(contract_game.get("selectorAxes")) == string_list(html_surface.get("selectorAxes"))
            and artifact_ok
            and planning_ok
            and contract_game.get("coverageTier") in tier_ids
            and game_id in used_by,
            f"{game_id} synthesis contract must match index.html and reference existing artifacts/docs when declared",
        )

    embedded_scripts = extract_embedded_scripts(index_html)
    add_check(
        checks,
        "html.embedded_scripts_exist",
        bool(embedded_scripts) and all(path_exists(root, path) for path in embedded_scripts),
        f"all embedded runtime mirror scripts referenced by index.html must exist; scripts={embedded_scripts}",
    )
    add_check(
        checks,
        "html.practical_warning_text",
        "exact chart ではなく" in index_html
        and "normalized repo bundle ではありません" in index_html
        and "solver exact" in index_html
        and "position 別の確定レンジではありません" in index_html,
        "UI metadata must preserve exact-vs-practical-vs-plan warning language",
    )
    add_check(
        checks,
        "html.plo8_inline_no_bundle_boundary",
        "const MIX_PLO8_OPEN_POSITION_PACKS" in index_html
        and html_surfaces.get("plo8", {}).get("coverageTier") == "research_frozen_no_bundle"
        and normalize_optional_path(html_surfaces.get("plo8", {}).get("repoArtifact")) == "",
        "PLO8 must remain an inline public-source no-bundle surface until a repo artifact is declared",
    )


def verify_public_source_assets(checks: list[CheckResult], root: Path) -> None:
    for game_id, rel_path in PUBLIC_SOURCE_ASSETS.items():
        try:
            payload = read_json_object(root / rel_path)
        except (OSError, json.JSONDecodeError, ValueError):
            payload = {}
        if game_id == "basil_826":
            scope = payload.get("scope") if isinstance(payload.get("scope"), dict) else {}
            ok = (
                isinstance(payload.get("hand_ranges"), dict)
                and bool(payload.get("hand_ranges"))
                and isinstance(payload.get("source_index"), dict)
                and bool(payload.get("source_index"))
                and scope.get("position_model") == "not_available_from_public_sources"
                and "exact UTG/HJ/CO/BTN/SB range matrix" in str(scope.get("source_boundary", ""))
            )
        else:
            ok = (
                isinstance(payload.get("positions"), dict)
                and bool(payload.get("positions"))
                and isinstance(payload.get("source_index"), dict)
                and bool(payload.get("source_index"))
                and isinstance(payload.get("collection_notes"), list)
            )
        add_check(
            checks,
            f"public_asset.{game_id}.shape",
            ok,
            f"{game_id} public-source asset must be valid and carry positions/source evidence or hand ranges",
        )
    try:
        stud8 = read_json_object(root / PUBLIC_SOURCE_ASSETS["stud8"])
        scope_text = json.dumps(stud8.get("scope", {}), sort_keys=True)
    except (OSError, json.JSONDecodeError, ValueError):
        scope_text = ""
    add_check(
        checks,
        "public_asset.stud8.not_solver",
        "not solver chart" in scope_text or "not a solver chart" in scope_text,
        "Stud8 public-source asset must explicitly avoid solver-chart claims",
    )


def verify_continuity_and_vacuous_check_fix(checks: list[CheckResult], root: Path) -> None:
    handoff = read_text(root / EXPECTED_FILES["handoff"])
    bootstrap = read_text(root / EXPECTED_FILES["bootstrap"])
    blocked_healthcheck = read_text(root / EXPECTED_FILES["blocked_healthcheck"])
    stale_needles = [
        "continuity_status: blocked_user_step",
        "blocked_no_source pending",
        "attach_artifact || blocked-family source-drop files",
    ]
    add_check(
        checks,
        "continuity.no_stale_blocked_step",
        not any(needle in handoff for needle in stale_needles)
        and "`continuity_status: completed`" in bootstrap
        and "continuity_status: completed" in handoff,
        "startup continuity must not reintroduce the obsolete blocked-family source-drop ask",
    )
    add_check(
        checks,
        "blocked_healthcheck.inactive_when_no_blocked_families",
        "inactive_no_blocked_families" in blocked_healthcheck
        and "not evidence that the current grounded-family display strategy is correct" in blocked_healthcheck,
        "blocked-family healthcheck must report inactive, not strategy proof, when no blocked families remain",
    )


def load_inputs(root: Path, checks: list[CheckResult]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for key, rel_path in EXPECTED_FILES.items():
        path = root / rel_path
        add_check(checks, f"input.{key}.exists", path.is_file(), f"required input exists at {rel_path}")
        if not path.is_file():
            continue
        if rel_path.endswith(".json"):
            try:
                loaded[key] = read_json_object(path)
                add_check(checks, f"input.{key}.json_valid", True, f"{rel_path} parses as a JSON object")
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                add_check(checks, f"input.{key}.json_valid", False, f"{rel_path} failed to parse: {exc}")
                loaded[key] = {}
        else:
            loaded[key] = read_text(path)
    return loaded


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    checks: list[CheckResult] = []
    loaded = load_inputs(root, checks)

    registry = loaded.get("registry", {})
    catalog = loaded.get("catalog", {})
    display_index = loaded.get("display_index", {})
    contract = loaded.get("synthesis_contract", {})
    grounding_gates_text = loaded.get("grounding_gates", "")
    coverage_matrix_text = loaded.get("coverage_matrix", "")
    index_html = loaded.get("index_html", "")

    if isinstance(registry, dict):
        verify_registry(checks, registry)
    if isinstance(catalog, dict) and isinstance(display_index, dict):
        verify_catalog_and_display_index(checks, root, catalog, display_index)
    if isinstance(grounding_gates_text, str) and isinstance(coverage_matrix_text, str):
        verify_markdown_claim_boundaries(checks, grounding_gates_text, coverage_matrix_text)
    verify_pushfold_lane(checks, root)
    if isinstance(contract, dict) and isinstance(index_html, str):
        verify_contract_and_html(checks, root, contract, index_html)
    verify_public_source_assets(checks, root)
    verify_continuity_and_vacuous_check_fix(checks, root)

    failed = [check for check in checks if check.status != "passed"]
    fixes = [
        "Blocked-family aggregate healthcheck reports inactive_no_blocked_families when there is no blocked-family work to exercise.",
        "Current strategy verifier checks registry, catalog, display index, bundle artifacts, UI contract, HTML surfaces, public-source assets, and continuity state together.",
        "Cross-game synthesis contract is aligned to index.html's visible game surfaces and declared artifacts.",
        "Startup continuity no longer asks for obsolete blocked-family source-drop files.",
    ]
    residual_risk = [
        "This verifier proves repo-local consistency and claim boundaries; it does not prove poker EV optimality.",
        "Article-derived practical coverage remains practical heuristic coverage, not exact solver or chart coverage.",
        "PLO8 remains an inline public-source no-bundle surface until a normalized repo artifact is intentionally added.",
        "Off-repo source truth cannot be revalidated without external source acquisition.",
    ]
    payload = {
        "strategyCheckVersion": STRATEGY_CHECK_VERSION,
        "repoRoot": display_path(root, root),
        "status": "passed" if not failed else "failed",
        "summary": {
            "checksTotal": len(checks),
            "checksPassed": len(checks) - len(failed),
            "checksFailed": len(failed),
            "failedCheckIds": [check.check_id for check in failed],
            "boundedConfidenceClaim": (
                "repo-local strategy boundary is verified"
                if not failed
                else "repo-local strategy boundary is not verified"
            ),
        },
        "loopholesClosed": [
            "vacuous zero-subtest blocked-family pass cannot be mistaken for current strategy evidence",
            "exact retained-source slices cannot be conflated with practical heuristic families",
            "AoF push/fold lane cannot silently enter the six-family mix display matrix",
            "visible public-source surfaces cannot silently drift away from the synthesis contract",
            "stale startup continuity cannot re-open the obsolete blocked-family source-drop step",
        ],
        "fixes": fixes,
        "residualRisk": residual_risk,
        "checks": [check.as_dict() for check in checks] if args.verbose or failed else [],
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include all individual check results, not only failures.",
    )
    return parser.parse_args()


def main() -> int:
    payload = build_payload(parse_args())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
