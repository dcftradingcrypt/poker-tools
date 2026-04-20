#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = REPO_ROOT / "index.html"
DEFAULT_BUNDLE = REPO_ROOT / "assets/pushfold/aof-bundle.v1.json"
DEFAULT_SAFETY = REPO_ROOT / "assets/pushfold/aof-bundle-safety.v1.json"
DEFAULT_REPORT = REPO_ROOT / "out/_codex/cc_high_2card_bundled_mode_verification.md"
NODE_CANDIDATES = (
    Path("/mnt/c/Program Files/nodejs/node.exe"),
    Path("/mnt/c/Program Files/Volta/node.exe"),
)
PROBES = (
    {
        "name": "unsafe_open_antes10_sb_2bb",
        "regime": "antes10",
        "bb": 2,
        "position": "SB",
        "secondaryPosition": "",
        "expectedClass": "unsafe",
    },
    {
        "name": "unsafe_call_tool10max_utg_sb_1bb",
        "regime": "tool10max_bb100_call",
        "bb": 1,
        "position": "UTG",
        "secondaryPosition": "SB",
        "expectedClass": "unsafe",
    },
    {
        "name": "safe_open_antes0_utg_2bb",
        "regime": "antes0",
        "bb": 2,
        "position": "UTG",
        "secondaryPosition": "",
        "expectedClass": "safe",
    },
    {
        "name": "safe_call_tool10max_utg_utg1_2bb",
        "regime": "tool10max_bb100_call",
        "bb": 2,
        "position": "UTG",
        "secondaryPosition": "UTG+1",
        "expectedClass": "safe",
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE))
    parser.add_argument("--safety-asset", default=str(DEFAULT_SAFETY))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser


def find_matching_delimiter(text: str, start_index: int, open_char: str, close_char: str) -> int:
    depth = 0
    mode = "normal"
    i = start_index
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if mode == "normal":
            if ch == "/" and nxt == "/":
                mode = "line_comment"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                mode = "block_comment"
                i += 2
                continue
            if ch == "'":
                mode = "single"
                i += 1
                continue
            if ch == '"':
                mode = "double"
                i += 1
                continue
            if ch == "`":
                mode = "template"
                i += 1
                continue
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return i
            i += 1
            continue
        if mode == "line_comment":
            if ch == "\n":
                mode = "normal"
            i += 1
            continue
        if mode == "block_comment":
            if ch == "*" and nxt == "/":
                mode = "normal"
                i += 2
                continue
            i += 1
            continue
        if mode in {"single", "double", "template"}:
            if ch == "\\":
                i += 2
                continue
            if (mode == "single" and ch == "'") or (mode == "double" and ch == '"') or (mode == "template" and ch == "`"):
                mode = "normal"
            i += 1
            continue
    raise RuntimeError(f"unmatched delimiter starting at {start_index}")


def find_matching_brace(text: str, open_brace_index: int) -> int:
    return find_matching_delimiter(text, open_brace_index, "{", "}")


def extract_function(source_text: str, function_name: str) -> str:
    signature = f"function {function_name}("
    start = source_text.find(signature)
    if start < 0:
        raise RuntimeError(f"missing function {function_name}")
    open_paren = source_text.find("(", start)
    if open_paren < 0:
        raise RuntimeError(f"missing parameter list for {function_name}")
    close_paren = find_matching_delimiter(source_text, open_paren, "(", ")")
    open_brace = source_text.find("{", close_paren)
    if open_brace < 0:
        raise RuntimeError(f"missing function body for {function_name}")
    close_brace = find_matching_brace(source_text, open_brace)
    return source_text[start : close_brace + 1]


def extract_const_object(source_text: str, const_name: str) -> str:
    signature = f"const {const_name} ="
    start = source_text.find(signature)
    if start < 0:
        raise RuntimeError(f"missing constant {const_name}")
    open_brace = source_text.find("{", start)
    if open_brace < 0:
        raise RuntimeError(f"missing object body for {const_name}")
    close_brace = find_matching_brace(source_text, open_brace)
    semicolon = source_text.find(";", close_brace)
    if semicolon < 0:
        raise RuntimeError(f"missing semicolon for {const_name}")
    return source_text[start : semicolon + 1]


def extract_const_statement(source_text: str, const_name: str) -> str:
    signature = f"const {const_name} ="
    start = source_text.find(signature)
    if start < 0:
        raise RuntimeError(f"missing constant {const_name}")
    semicolon = source_text.find(";", start)
    if semicolon < 0:
        raise RuntimeError(f"missing semicolon for {const_name}")
    return source_text[start : semicolon + 1]


def windows_to_wsl_path(raw_path: str) -> Path:
    normalized = raw_path.strip().replace("\\", "/")
    if len(normalized) >= 2 and normalized[1] == ":":
        drive = normalized[0].lower()
        tail = normalized[2:].lstrip("/")
        return Path(f"/mnt/{drive}/{tail}")
    return Path(normalized)


def wsl_to_windows_path(path: Path) -> str:
    raw = path.as_posix()
    if raw.startswith("/mnt/") and len(raw) > 6 and raw[6] == "/":
        drive = raw[5].upper()
        tail = raw[7:].replace("/", "\\")
        return f"{drive}:\\{tail}"
    return raw.replace("/", "\\")


def resolve_node_executable() -> Path:
    env_path = os.environ.get("NODE_EXE", "").strip()
    if env_path:
        env_candidate = windows_to_wsl_path(env_path)
        if env_candidate.exists():
            return env_candidate
    for candidate in NODE_CANDIDATES:
        if candidate.exists():
            return candidate
    proc = subprocess.run(
        ["cmd.exe", "/c", "where node.exe"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            candidate = windows_to_wsl_path(line)
            if candidate.exists():
                return candidate
    raise RuntimeError("node executable not found for bundled-mode verifier")


def build_js_harness(index_text: str, bundle_path: Path, safety_path: Path, probes: list[dict] | tuple[dict, ...] = PROBES) -> str:
    bundle_fs_path = wsl_to_windows_path(bundle_path)
    safety_fs_path = wsl_to_windows_path(safety_path)
    snippets = [
        extract_const_statement(index_text, "PUSHFOLD_JENNIFEAR_FAMILY_ID"),
        extract_const_statement(index_text, "PUSHFOLD_JENNIFEAR_FAMILY_LABEL"),
        extract_const_statement(index_text, "PUSHFOLD_JENNIFEAR_FAMILY_DESCRIPTION"),
        extract_const_statement(index_text, "PUSHFOLD_TOOL_FAMILY_ID"),
        extract_const_statement(index_text, "PUSHFOLD_TOOL_FAMILY_LABEL"),
        extract_const_statement(index_text, "PUSHFOLD_TOOL_FAMILY_DESCRIPTION"),
        extract_const_object(index_text, "PUSHFOLD_DEFAULT_SEMANTICS"),
        "const PUSHFOLD_DEFAULT_REGIME_ID = PUSHFOLD_DEFAULT_SEMANTICS.regimeId;",
        "const pushfoldRuntimeState = { bundledAssetPath: 'assets/pushfold/aof-bundle.v1.json' };",
        extract_function(index_text, "buildPushfoldSafetyLookupKey"),
        extract_function(index_text, "readPushfoldUnsafeTupleRecord"),
        extract_function(index_text, "normalizePushfoldLoadedGuard"),
        extract_function(index_text, "normalizePushfoldSemantics"),
        extract_function(index_text, "buildPushfoldUnsafeTuplePayload"),
        extract_function(index_text, "readPushfoldBundledRegimeEntry"),
        extract_function(index_text, "buildPushfoldBundledStackPayload"),
    ]
    return "\n".join(
        [
            "const fs = require('fs');",
            f"const bundlePayload = JSON.parse(fs.readFileSync({json.dumps(bundle_fs_path)}, 'utf8'));",
            f"const safetyPayload = JSON.parse(fs.readFileSync({json.dumps(safety_fs_path)}, 'utf8'));",
            *snippets,
            f"const probes = {json.dumps(list(probes), ensure_ascii=False)};",
            """
function runBundledProbe(probe) {
  const secondaryPosition = probe.secondaryPosition || '';
  const unsafeTupleRecord = readPushfoldUnsafeTupleRecord(
    safetyPayload,
    probe.regime,
    probe.bb,
    probe.position,
    secondaryPosition
  );
  let payload = buildPushfoldBundledStackPayload(
    bundlePayload,
    probe.regime,
    probe.bb,
    probe.position,
    secondaryPosition
  );
  if (unsafeTupleRecord) {
    payload = buildPushfoldUnsafeTuplePayload({
      bb: probe.bb,
      position: probe.position,
      secondaryPosition,
      unsafeTupleRecord,
      selectedRegime: probe.regime,
      availableRegimes: payload.availableRegimes,
      secondaryPositionsByPosition: payload.secondaryPositionsByPosition,
      semantics: payload.semantics,
      sourceReference: pushfoldRuntimeState.bundledAssetPath,
    });
  }
  const loadedGuard = normalizePushfoldLoadedGuard({
    status: payload.status,
    lookupKeyTuple: payload.lookupKeyTuple,
    exactSemanticsAuthority: payload.exactSemanticsAuthority,
    lossModes: payload.lossModes,
    safetyGateNote: payload.safetyGateNote,
  });
  return {
    name: probe.name,
    expectedClass: probe.expectedClass,
    regime: probe.regime,
    bb: probe.bb,
    position: probe.position,
    secondaryPosition,
    unsafeTupleRecord: unsafeTupleRecord ? {
      lookupKeyTuple: unsafeTupleRecord.lookupKeyTuple,
      comparisonClass: unsafeTupleRecord.comparisonClass,
      bundleMembershipSafe: unsafeTupleRecord.bundleMembershipSafe === true,
      exactSemanticsAuthority: unsafeTupleRecord.exactSemanticsAuthority,
      lossModes: Array.isArray(unsafeTupleRecord.lossModes) ? unsafeTupleRecord.lossModes : [],
      note: unsafeTupleRecord.note || '',
    } : null,
    payload: {
      status: payload.status,
      categoryCount: Number.isInteger(payload.categoryCount) ? payload.categoryCount : 0,
      bundleMembershipSafe: payload.bundleMembershipSafe === true,
      nonAuthoritative: payload.nonAuthoritative === true,
      comparisonClass: typeof payload.comparisonClass === 'string' ? payload.comparisonClass : '',
      exactSemanticsAuthority: typeof payload.exactSemanticsAuthority === 'string' ? payload.exactSemanticsAuthority : '',
      lossModes: Array.isArray(payload.lossModes) ? payload.lossModes : [],
      lookupKeyTuple: typeof payload.lookupKeyTuple === 'string' ? payload.lookupKeyTuple : '',
      safetyGateNote: typeof payload.safetyGateNote === 'string' ? payload.safetyGateNote : '',
      selectedRegime: typeof payload.selectedRegime === 'string' ? payload.selectedRegime : '',
      semanticsSourceReference: typeof payload.semantics?.sourceReference === 'string' ? payload.semantics.sourceReference : '',
      sampleCategories: Array.isArray(payload.categories) ? payload.categories.slice(0, 12) : [],
    },
    loadedGuard: loadedGuard ? {
      status: loadedGuard.status,
      lookupKeyTuple: loadedGuard.lookupKeyTuple,
      exactSemanticsAuthority: loadedGuard.exactSemanticsAuthority,
      lossModes: loadedGuard.lossModes,
      safetyGateNote: loadedGuard.safetyGateNote,
    } : null,
    exactObservable: loadedGuard
      ? {
          kind: 'loadedGuard',
          status: loadedGuard.status,
          lookupKeyTuple: loadedGuard.lookupKeyTuple,
          exactSemanticsAuthority: loadedGuard.exactSemanticsAuthority,
          lossModes: loadedGuard.lossModes,
          safetyGateNote: loadedGuard.safetyGateNote,
        }
      : {
          kind: 'payload',
          status: payload.status,
          categoryCount: Number.isInteger(payload.categoryCount) ? payload.categoryCount : 0,
        },
  };
}

const results = probes.map(runBundledProbe);
console.log(JSON.stringify({
  method: 'index_html_function_execution_via_node',
  bundlePath: pushfoldRuntimeState.bundledAssetPath,
  safetyPath: %s,
  results,
}, null, 2));
"""
            % json.dumps("assets/pushfold/aof-bundle-safety.v1.json"),
        ]
    )


def run_node_harness(node_path: Path, harness_text: str) -> dict:
    proc = subprocess.run(
        [str(node_path), "-e", harness_text],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bundled guard harness failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(proc.stdout)


def run_probe_set(index_path: Path, bundle_path: Path, safety_path: Path, probes: list[dict] | tuple[dict, ...]) -> tuple[Path, dict]:
    index_text = index_path.read_text(encoding="utf-8")
    node_path = resolve_node_executable()
    harness_text = build_js_harness(index_text, bundle_path, safety_path, probes)
    return node_path, run_node_harness(node_path, harness_text)


def assert_probe_results(results: list[dict]) -> None:
    by_name = {entry["name"]: entry for entry in results}
    unsafe_open = by_name["unsafe_open_antes10_sb_2bb"]
    if unsafe_open["payload"]["status"] != "unsafe_tuple_non_authoritative":
        raise RuntimeError("unsafe bundled open probe did not return unsafe_tuple_non_authoritative")
    if unsafe_open["loadedGuard"] is None or unsafe_open["loadedGuard"]["status"] != "unsafe_tuple_non_authoritative":
        raise RuntimeError("unsafe bundled open probe did not surface loadedGuard")
    if "bundle_missing_membership" not in unsafe_open["payload"]["lossModes"]:
        raise RuntimeError("unsafe bundled open probe missing bundle_missing_membership")

    unsafe_call = by_name["unsafe_call_tool10max_utg_sb_1bb"]
    if unsafe_call["payload"]["status"] != "unsafe_tuple_non_authoritative":
        raise RuntimeError("unsafe bundled call probe did not return unsafe_tuple_non_authoritative")
    if unsafe_call["loadedGuard"] is None or unsafe_call["loadedGuard"]["status"] != "unsafe_tuple_non_authoritative":
        raise RuntimeError("unsafe bundled call probe did not surface loadedGuard")
    required_loss_modes = {"bundle_missing_membership", "dropped_percentage_prefix"}
    if not required_loss_modes.issubset(set(unsafe_call["payload"]["lossModes"])):
        raise RuntimeError("unsafe bundled call probe missing expected loss modes")

    safe_open = by_name["safe_open_antes0_utg_2bb"]
    if safe_open["payload"]["status"] != "ok" or safe_open["loadedGuard"] is not None:
        raise RuntimeError("safe bundled open probe did not stay on the normal ok path")
    if safe_open["payload"]["categoryCount"] != 62:
        raise RuntimeError("safe bundled open probe category count mismatch")

    safe_call = by_name["safe_call_tool10max_utg_utg1_2bb"]
    if safe_call["payload"]["status"] != "ok" or safe_call["loadedGuard"] is not None:
        raise RuntimeError("safe bundled call probe did not stay on the normal ok path")
    if safe_call["payload"]["categoryCount"] != 153:
        raise RuntimeError("safe bundled call probe category count mismatch")


def format_probe_label(result: dict) -> str:
    if result.get("secondaryPosition"):
        return f"{result['regime']} / (stack={result['bb']}, position={result['position']}, secondary={result['secondaryPosition']})"
    return f"{result['regime']} / (stack={result['bb']}, position={result['position']})"


def build_report(payload: dict, node_path: Path, index_path: Path, bundle_path: Path, safety_path: Path) -> str:
    results = payload["results"]
    lines = [
        "# cc_high / 2-card bundled-mode verification",
        "",
        "## Execution method",
        "",
        f"- Direct-execution method: `{payload['method']}`.",
        f"- JS runtime: `{node_path.as_posix()}`.",
        f"- Client source executed: [index.html]({index_path.as_posix()}).",
        f"- Bundle asset: [aof-bundle.v1.json]({bundle_path.as_posix()}).",
        f"- Safety asset: [aof-bundle-safety.v1.json]({safety_path.as_posix()}).",
        "- Verification path: execute the shipped bundled-mode selection and safety-gate functions extracted from `index.html` in Node, then capture the exact emitted payload shape and `loadedGuard` state for each concrete tuple.",
        "",
        "## Probe results",
        "",
        "| probe | expected_class | payload_status | loaded_guard_status | category_count | exact_observable | loss_modes | note |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for result in results:
        loaded_guard_status = result["loadedGuard"]["status"] if result.get("loadedGuard") else "none"
        observable = result["exactObservable"]["kind"]
        loss_modes = ", ".join(result["payload"]["lossModes"]) or "none"
        note = result["payload"]["safetyGateNote"] or "normal ok payload"
        lines.append(
            f"| `{format_probe_label(result)}` | `{result['expectedClass']}` | `{result['payload']['status']}` | "
            f"`{loaded_guard_status}` | {result['payload']['categoryCount']} | `{observable}` | `{loss_modes}` | {note} |"
        )
    lines.extend(
        [
            "",
            "## Exact observables",
            "",
            f"- Unsafe bundled open probe: `loadedGuard.status = {results[0]['loadedGuard']['status']}` with `lookupKeyTuple = {results[0]['loadedGuard']['lookupKeyTuple']}`.",
            f"- Unsafe bundled call probe: `loadedGuard.status = {results[1]['loadedGuard']['status']}` with `lookupKeyTuple = {results[1]['loadedGuard']['lookupKeyTuple']}`.",
            f"- Safe bundled open control: `payload.status = {results[2]['payload']['status']}` and `categoryCount = {results[2]['payload']['categoryCount']}`.",
            f"- Safe bundled call control: `payload.status = {results[3]['payload']['status']}` and `categoryCount = {results[3]['payload']['categoryCount']}`.",
            "",
            "## Verdict",
            "",
            "- Bundled mode is directly probe-verified in this lane.",
            "- Representative unsafe tuples do not surface as authoritative empty results; they surface as `unsafe_tuple_non_authoritative` with a non-null `loadedGuard` observable.",
            "- Representative safe tuples stay on the normal `status=ok` bundled payload path.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    index_path = Path(args.index)
    bundle_path = Path(args.bundle)
    safety_path = Path(args.safety_asset)
    report_path = Path(args.report)

    node_path, result_payload = run_probe_set(index_path, bundle_path, safety_path, PROBES)
    results = result_payload.get("results", [])
    if not isinstance(results, list) or len(results) != len(PROBES):
        raise RuntimeError("bundled-mode verifier returned an unexpected result shape")
    assert_probe_results(results)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(result_payload, node_path, index_path, bundle_path, safety_path),
        encoding="utf-8",
    )
    print(f"bundled_mode_verification_report={report_path}")
    print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
