#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import verify_pushfold_bundled_guard as bundled_verifier
import verify_pushfold_local_runtime as bridge_verifier


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = REPO_ROOT / "index.html"
DEFAULT_STARTER = REPO_ROOT / "scripts/start_pushfold_local.py"
DEFAULT_BUNDLE = REPO_ROOT / "assets/pushfold/aof-bundle.v1.json"
DEFAULT_SAFETY = REPO_ROOT / "assets/pushfold/aof-bundle-safety.v1.json"
DEFAULT_REPORT = REPO_ROOT / "out/_codex/cc_high_2card_runtime_guard_regression.md"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_STATIC_PORT = 8766
DEFAULT_BRIDGE_PORT = 8765
DEFAULT_HEALTH_TIMEOUT = 15.0
DEFAULT_POLL_INTERVAL = 0.25
DEFAULT_REGIMES_ROOT = REPO_ROOT / "out/_private/pushfold_real_data_regimes"
DEFAULT_PACK = REPO_ROOT / "out/_private/pushfold_real_data/pack.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--starter", default=str(DEFAULT_STARTER))
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE))
    parser.add_argument("--safety-asset", default=str(DEFAULT_SAFETY))
    parser.add_argument("--pack", default=str(DEFAULT_PACK))
    parser.add_argument("--regimes-root", default=str(DEFAULT_REGIMES_ROOT))
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--static-port", type=int, default=DEFAULT_STATIC_PORT)
    parser.add_argument("--bridge-port", type=int, default=DEFAULT_BRIDGE_PORT)
    parser.add_argument("--health-timeout", type=float, default=DEFAULT_HEALTH_TIMEOUT)
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_lookup_key(lookup_key: str) -> tuple[int, str, str]:
    parts = str(lookup_key).split("|")
    if len(parts) not in {2, 3}:
        raise RuntimeError(f"unexpected lookup key format: {lookup_key}")
    bb = int(parts[0])
    position = parts[1]
    secondary_position = parts[2] if len(parts) == 3 else ""
    return bb, position, secondary_position


def enumerate_unsafe_probes(safety_payload: dict[str, Any]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    raw_regimes = safety_payload.get("regimes", {})
    if not isinstance(raw_regimes, dict):
        raise RuntimeError("invalid safety asset: missing regimes")
    for regime_id, regime_entry in raw_regimes.items():
        if not isinstance(regime_entry, dict):
            continue
        unsafe_lookup_keys = regime_entry.get("unsafeLookupKeys", {})
        if not isinstance(unsafe_lookup_keys, dict):
            continue
        for index, lookup_key in enumerate(unsafe_lookup_keys.keys(), start=1):
            bb, position, secondary_position = parse_lookup_key(lookup_key)
            probes.append(
                {
                    "name": f"unsafe::{regime_id}::{index}",
                    "regime": regime_id,
                    "bb": bb,
                    "position": position,
                    "secondaryPosition": secondary_position,
                    "expectedClass": "unsafe",
                }
            )
    return probes


def derive_safe_control(entry: dict[str, Any], unsafe_lookup_keys: set[str]) -> dict[str, Any]:
    regime_id = str(entry.get("id", "")).strip()
    catalog = entry.get("catalog", {})
    positions = entry.get("positions", [])
    secondary_positions_by_position = entry.get("secondaryPositionsByPosition", {})
    if not isinstance(catalog, dict) or not isinstance(positions, list):
        raise RuntimeError(f"invalid regime catalog: {regime_id}")
    for bb in entry.get("stacks", []):
        stack_map = catalog.get(str(bb), catalog.get(bb))
        if not isinstance(stack_map, dict):
            continue
        for position in positions:
            raw_value = stack_map.get(position)
            if isinstance(raw_value, list):
                lookup_key = f"{bb}|{position}"
                if lookup_key in unsafe_lookup_keys or not raw_value:
                    continue
                return {
                    "name": f"safe::{regime_id}",
                    "regime": regime_id,
                    "bb": int(bb),
                    "position": position,
                    "secondaryPosition": "",
                    "expectedClass": "safe",
                }
            if not isinstance(raw_value, dict):
                continue
            secondary_candidates = secondary_positions_by_position.get(position, list(raw_value.keys()))
            for secondary_position in secondary_candidates:
                categories = raw_value.get(secondary_position)
                lookup_key = f"{bb}|{position}|{secondary_position}"
                if lookup_key in unsafe_lookup_keys or not isinstance(categories, list) or not categories:
                    continue
                return {
                    "name": f"safe::{regime_id}",
                    "regime": regime_id,
                    "bb": int(bb),
                    "position": position,
                    "secondaryPosition": secondary_position,
                    "expectedClass": "safe",
                }
    raise RuntimeError(f"no safe control found for regime {regime_id}")


def enumerate_safe_controls(bundle_payload: dict[str, Any], safety_payload: dict[str, Any]) -> list[dict[str, Any]]:
    regimes = bundle_payload.get("regimes", {})
    safety_regimes = safety_payload.get("regimes", {})
    if not isinstance(regimes, dict):
        raise RuntimeError("invalid bundle payload: missing regimes")
    controls: list[dict[str, Any]] = []
    for regime_id, entry in regimes.items():
        if not isinstance(entry, dict):
            continue
        safety_entry = safety_regimes.get(regime_id, {}) if isinstance(safety_regimes, dict) else {}
        unsafe_lookup_keys = set()
        if isinstance(safety_entry, dict):
            raw_unsafe = safety_entry.get("unsafeLookupKeys", {})
            if isinstance(raw_unsafe, dict):
                unsafe_lookup_keys = {str(key) for key in raw_unsafe.keys()}
        controls.append(derive_safe_control(entry, unsafe_lookup_keys))
    return controls


def verify_bundled_results(results: list[dict[str, Any]]) -> list[str]:
    mismatches: list[str] = []
    for result in results:
        label = bundled_verifier.format_probe_label(result)
        expected_class = result.get("expectedClass")
        payload = result.get("payload", {})
        loaded_guard = result.get("loadedGuard")
        if expected_class == "unsafe":
            if payload.get("status") != "unsafe_tuple_non_authoritative":
                mismatches.append(f"bundled unsafe status mismatch: {label}")
            if not isinstance(loaded_guard, dict) or loaded_guard.get("status") != "unsafe_tuple_non_authoritative":
                mismatches.append(f"bundled unsafe loadedGuard mismatch: {label}")
        elif expected_class == "safe":
            if payload.get("status") != "ok":
                mismatches.append(f"bundled safe status mismatch: {label}")
            if loaded_guard is not None:
                mismatches.append(f"bundled safe loadedGuard should be null: {label}")
            if int(payload.get("categoryCount", 0)) <= 0:
                mismatches.append(f"bundled safe categoryCount mismatch: {label}")
    return mismatches


def build_bridge_probe_url(base_url: str, probe: dict[str, Any]) -> str:
    return bridge_verifier.build_stack_probe_url(
        base_url,
        str(probe["regime"]),
        int(probe["bb"]),
        str(probe["position"]),
        str(probe.get("secondaryPosition", "")),
    )


def run_bridge_probe_set(args: argparse.Namespace, probes: list[dict[str, Any]]) -> dict[str, Any]:
    starter_path = Path(args.starter)
    if not starter_path.exists():
        raise RuntimeError(f"starter script not found: {starter_path}")
    bridge_base = f"http://{args.host}:{args.bridge_port}"
    index_url = f"http://{args.host}:{args.static_port}/index.html"
    health_url = f"{bridge_base}/api/health?regime=antes0"
    with tempfile.TemporaryDirectory(prefix="cc_high_2card_runtime_guard_") as tmp_dir:
        launcher_log = Path(tmp_dir) / "launcher.log"
        starter_cmd = [
            sys.executable,
            str(starter_path),
            "--host",
            args.host,
            "--static-port",
            str(args.static_port),
            "--bridge-port",
            str(args.bridge_port),
            "--health-timeout",
            str(args.health_timeout),
            "--poll-interval",
            str(args.poll_interval),
            "--pack",
            args.pack,
            "--regimes-root",
            args.regimes_root,
            "--index",
            args.index,
            "--safety-asset",
            args.safety_asset,
            "--pushfold-regime",
            "antes0",
        ]
        proc: subprocess.Popen[str] | None = None
        try:
            with launcher_log.open("w", encoding="utf-8") as log_handle:
                log_handle.write(f"starter_cmd={' '.join(starter_cmd)}\n")
                log_handle.flush()
                proc = subprocess.Popen(
                    starter_cmd,
                    cwd=str(REPO_ROOT),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                bridge_verifier.wait_until_ready(proc, index_url, health_url, args.health_timeout, args.poll_interval)
            results = []
            for probe in probes:
                url = build_bridge_probe_url(bridge_base, probe)
                status, _headers, payload, payload_size = bridge_verifier.load_json_response(url)
                summary = bridge_verifier.summarize_named_probe(probe["name"], url, status, payload, payload_size)
                summary["regime"] = str(probe["regime"])
                summary["expectedClass"] = probe["expectedClass"]
                summary["bb"] = int(probe["bb"])
                summary["position"] = str(probe["position"])
                summary["secondaryPosition"] = str(probe.get("secondaryPosition", ""))
                results.append(summary)
            return {
                "method": "start_pushfold_local_http_stack_probe_set",
                "bridgeBase": bridge_base,
                "launcherLog": launcher_log.read_text(encoding="utf-8"),
                "results": results,
            }
        finally:
            if proc is not None:
                bridge_verifier.terminate_process(proc)


def verify_bridge_results(results: list[dict[str, Any]]) -> list[str]:
    mismatches: list[str] = []
    for result in results:
        label = bundled_verifier.format_probe_label(result)
        expected_class = result.get("expectedClass")
        if expected_class == "unsafe":
            if result.get("payloadStatus") != "unsafe_tuple_non_authoritative":
                mismatches.append(f"bridge unsafe status mismatch: {label}")
            if result.get("bundleMembershipSafe") is not False:
                mismatches.append(f"bridge unsafe bundleMembershipSafe mismatch: {label}")
            if result.get("nonAuthoritative") is not True:
                mismatches.append(f"bridge unsafe nonAuthoritative mismatch: {label}")
        elif expected_class == "safe":
            if result.get("payloadStatus") != "ok":
                mismatches.append(f"bridge safe status mismatch: {label}")
            if int(result.get("categoryCount", 0)) <= 0:
                mismatches.append(f"bridge safe categoryCount mismatch: {label}")
    return mismatches


def summarize_by_regime(results: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for result in results:
        regime = str(result["regime"])
        bucket = summary.setdefault(
            regime,
            {"unsafe_total": 0, "unsafe_pass": 0, "unsafe_fail": 0, "safe_total": 0, "safe_pass": 0, "safe_fail": 0},
        )
        expected_class = result.get("expectedClass")
        passed = bool(result.get("passed"))
        if expected_class == "unsafe":
            bucket["unsafe_total"] += 1
            bucket["unsafe_pass" if passed else "unsafe_fail"] += 1
        else:
            bucket["safe_total"] += 1
            bucket["safe_pass" if passed else "safe_fail"] += 1
    return summary


def render_result_label(result: dict[str, Any]) -> str:
    return bundled_verifier.format_probe_label(result)


def build_report(
    bundled_payload: dict[str, Any],
    bridge_payload: dict[str, Any],
    bundled_results: list[dict[str, Any]],
    bridge_results: list[dict[str, Any]],
    total_unsafe: int,
    total_safe_controls: int,
) -> str:
    bundled_summary = summarize_by_regime(bundled_results)
    bridge_summary = summarize_by_regime(bridge_results)
    lines = [
        "# cc_high / 2-card runtime guard regression",
        "",
        "## Execution methods",
        "",
        f"- Bundled mode: `{bundled_payload['method']}` via [verify_pushfold_bundled_guard.py]({(REPO_ROOT / 'scripts/verify_pushfold_bundled_guard.py').as_posix()}).",
        f"- Launcher-backed bridge mode: `{bridge_payload['method']}` via [start_pushfold_local.py]({(REPO_ROOT / 'scripts/start_pushfold_local.py').as_posix()}) and `/api/stack` probes.",
        f"- Unsafe tuples enumerated from [aof-bundle-safety.v1.json]({(REPO_ROOT / 'assets/pushfold/aof-bundle-safety.v1.json').as_posix()}): {total_unsafe}.",
        f"- Safe controls selected from the shipped bundle: {total_safe_controls} total, one per visible regime.",
        "",
        "## Overview matrix",
        "",
        "| surface | regime | unsafe_total | unsafe_pass | unsafe_fail | safe_controls_ok | safe_controls_fail | representative_observable |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    regimes = sorted(set(bundled_summary) | set(bridge_summary))
    for regime in regimes:
        bundled_bucket = bundled_summary.get(regime, {})
        bridge_bucket = bridge_summary.get(regime, {})
        bundled_rep = next(result for result in bundled_results if result["regime"] == regime)
        bridge_rep = next(result for result in bridge_results if result["regime"] == regime)
        lines.append(
            f"| `bundled_mode` | `{regime}` | {bundled_bucket.get('unsafe_total', 0)} | {bundled_bucket.get('unsafe_pass', 0)} | "
            f"{bundled_bucket.get('unsafe_fail', 0)} | {bundled_bucket.get('safe_pass', 0)} | {bundled_bucket.get('safe_fail', 0)} | "
            f"`{bundled_rep['payload']['status']}` / `{bundled_rep['exactObservable']['kind']}` |"
        )
        lines.append(
            f"| `launcher_bridge` | `{regime}` | {bridge_bucket.get('unsafe_total', 0)} | {bridge_bucket.get('unsafe_pass', 0)} | "
            f"{bridge_bucket.get('unsafe_fail', 0)} | {bridge_bucket.get('safe_pass', 0)} | {bridge_bucket.get('safe_fail', 0)} | "
            f"`{bridge_rep['payloadStatus']}` / `bundleMembershipSafe={bridge_rep.get('bundleMembershipSafe')}` |"
        )
    lines.extend(
        [
            "",
            "## Representative results",
            "",
        ]
    )
    unsafe_bundled = next(result for result in bundled_results if result["expectedClass"] == "unsafe")
    unsafe_bridge = next(result for result in bridge_results if result["expectedClass"] == "unsafe")
    safe_bundled = next(result for result in bundled_results if result["expectedClass"] == "safe")
    safe_bridge = next(result for result in bridge_results if result["expectedClass"] == "safe")
    lines.extend(
        [
            f"- Bundled unsafe: `{render_result_label(unsafe_bundled)}` -> `payload.status={unsafe_bundled['payload']['status']}`, `loadedGuard.status={unsafe_bundled['loadedGuard']['status']}`, `lossModes={unsafe_bundled['payload']['lossModes']}`.",
            f"- Bridge unsafe: `{render_result_label(unsafe_bridge)}` -> `payloadStatus={unsafe_bridge['payloadStatus']}`, `bundleMembershipSafe={unsafe_bridge['bundleMembershipSafe']}`, `nonAuthoritative={unsafe_bridge['nonAuthoritative']}`, `lossModes={unsafe_bridge['lossModes']}`.",
            f"- Bundled safe control: `{render_result_label(safe_bundled)}` -> `payload.status={safe_bundled['payload']['status']}`, `loadedGuard={safe_bundled['loadedGuard']}`, `categoryCount={safe_bundled['payload']['categoryCount']}`.",
            f"- Bridge safe control: `{render_result_label(safe_bridge)}` -> `payloadStatus={safe_bridge['payloadStatus']}`, `categoryCount={safe_bridge['categoryCount']}`.",
            "",
            "## Mismatches",
            "",
        ]
    )
    bundled_failures = [result for result in bundled_results if not result["passed"]]
    bridge_failures = [result for result in bridge_results if not result["passed"]]
    if not bundled_failures and not bridge_failures:
        lines.append("- None. All enumerated unsafe tuples were correctly gated across both surfaces, and every chosen safe control remained on the normal `ok` path.")
    else:
        for result in bundled_failures:
            lines.append(f"- Bundled mismatch: `{render_result_label(result)}` -> {result['failureReason']}")
        for result in bridge_failures:
            lines.append(f"- Bridge mismatch: `{render_result_label(result)}` -> {result['failureReason']}")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- Bundled mode: {sum(1 for result in bundled_results if result['expectedClass'] == 'unsafe' and result['passed'])}/{total_unsafe} unsafe tuples correctly gated; "
            f"{sum(1 for result in bundled_results if result['expectedClass'] == 'safe' and result['passed'])}/{total_safe_controls} safe controls stayed `status=ok`.",
            f"- Launcher-backed bridge mode: {sum(1 for result in bridge_results if result['expectedClass'] == 'unsafe' and result['passed'])}/{total_unsafe} unsafe tuples correctly gated; "
            f"{sum(1 for result in bridge_results if result['expectedClass'] == 'safe' and result['passed'])}/{total_safe_controls} safe controls stayed `status=ok`.",
        ]
    )
    if not bundled_failures and not bridge_failures:
        lines.append("- Acceptance result: PASS. No audited surface remains risk-bearing in this regression lane.")
    else:
        lines.append("- Acceptance result: FAIL. At least one tuple did not satisfy the runtime guard contract.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    bundle_path = Path(args.bundle)
    safety_path = Path(args.safety_asset)
    index_path = Path(args.index)
    report_path = Path(args.report)

    bundle_payload = load_json(bundle_path)
    safety_payload = load_json(safety_path)
    unsafe_probes = enumerate_unsafe_probes(safety_payload)
    safe_controls = enumerate_safe_controls(bundle_payload, safety_payload)
    all_probes = unsafe_probes + safe_controls

    _node_path, bundled_payload = bundled_verifier.run_probe_set(index_path, bundle_path, safety_path, all_probes)
    bundled_results = bundled_payload.get("results", [])
    if not isinstance(bundled_results, list):
        raise RuntimeError("bundled regression payload missing results")
    bundled_mismatches = set(verify_bundled_results(bundled_results))
    for result in bundled_results:
        label = render_result_label(result)
        failure_reason = next((reason for reason in bundled_mismatches if label in reason), "")
        result["passed"] = not bool(failure_reason)
        result["failureReason"] = failure_reason

    bridge_payload = run_bridge_probe_set(args, all_probes)
    bridge_results = bridge_payload.get("results", [])
    if not isinstance(bridge_results, list):
        raise RuntimeError("bridge regression payload missing results")
    bridge_mismatches = set(verify_bridge_results(bridge_results))
    for result in bridge_results:
        label = render_result_label(result)
        failure_reason = next((reason for reason in bridge_mismatches if label in reason), "")
        result["passed"] = not bool(failure_reason)
        result["failureReason"] = failure_reason

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(
            bundled_payload,
            bridge_payload,
            bundled_results,
            bridge_results,
            total_unsafe=len(unsafe_probes),
            total_safe_controls=len(safe_controls),
        ),
        encoding="utf-8",
    )

    print(f"runtime_guard_regression_report={report_path}")
    print(
        json.dumps(
            {
                "unsafeTupleCount": len(unsafe_probes),
                "safeControlCount": len(safe_controls),
                "bundledFailures": len([result for result in bundled_results if not result["passed"]]),
                "bridgeFailures": len([result for result in bridge_results if not result["passed"]]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not bundled_mismatches and not bridge_mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
