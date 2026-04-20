#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPO_ROOT / "out/_private/pushfold_real_data/pack.json"
DEFAULT_INDEX = REPO_ROOT / "index.html"
DEFAULT_STARTER = REPO_ROOT / "scripts/start_pushfold_local.py"
DEFAULT_SAFETY_ASSET = REPO_ROOT / "assets/pushfold/aof-bundle-safety.v1.json"
SOURCE_PATH = "scripts/start_pushfold_local.py"
SOURCE_KIND = "local_bootstrap_bridge_consumer_path"
STATUS_ID = "FOUND_LOCAL_UI_BRIDGE_CONSUMER"
UI_MARKERS = [
    "pushfold-family-select",
    "pushfold-load-btn",
    "pushfold-position-select",
    "pushfold-refresh-btn",
    "initPushfoldRuntimeBridge",
    "loadPushfoldRangeFromBridge",
    "pushfold-runtime-source-missing-chip",
]
REPRESENTATIVE_PROBES = (
    {
        "name": "safeOpenControl",
        "regime": "antes0",
        "bb": 2,
        "position": "UTG",
        "secondaryPosition": "",
    },
    {
        "name": "unsafeOpenGuard",
        "regime": "antes10",
        "bb": 2,
        "position": "SB",
        "secondaryPosition": "",
    },
    {
        "name": "safeCallControl",
        "regime": "tool10max_bb100_call",
        "bb": 2,
        "position": "UTG",
        "secondaryPosition": "UTG+1",
    },
    {
        "name": "unsafeCallGuard",
        "regime": "tool10max_bb100_call",
        "bb": 1,
        "position": "UTG",
        "secondaryPosition": "SB",
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--static-port", type=int, default=8766)
    parser.add_argument("--bridge-port", type=int, default=8765)
    parser.add_argument("--health-timeout", type=float, default=15.0)
    parser.add_argument("--poll-interval", type=float, default=0.25)
    parser.add_argument("--probe-position", default="UTG")
    parser.add_argument("--probe-secondary-position", default="")
    parser.add_argument("--probe-min-bb", type=int, default=2)
    parser.add_argument("--probe-max-bb", type=int, default=20)
    parser.add_argument("--probe-regime", default="antes0")
    parser.add_argument("--pack", default=str(DEFAULT_PACK))
    parser.add_argument("--regimes-root", default=str(REPO_ROOT / "out/_private/pushfold_real_data_regimes"))
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--starter", default=str(DEFAULT_STARTER))
    parser.add_argument("--safety-asset", default=str(DEFAULT_SAFETY_ASSET))
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--strict-gate-report", type=Path)
    return parser


def http_request(url: str, method: str = "GET", headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    request = Request(url, method=method, headers=headers or {})
    with urlopen(request, timeout=5.0) as response:
        status = getattr(response, "status", response.getcode())
        body = response.read()
        response_headers = {key: value for key, value in response.headers.items()}
        return status, response_headers, body


def probe_ready(url: str) -> bool:
    try:
        status, _headers, _body = http_request(url, headers={"Cache-Control": "no-store"})
        return 200 <= status < 400
    except (HTTPError, URLError, TimeoutError, OSError):
        return False


def wait_until_ready(proc: subprocess.Popen[str], ui_url: str, health_url: str, timeout: float, poll_interval: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"launcher exited before ready with code {proc.returncode}")
        if probe_ready(ui_url) and probe_ready(health_url):
            return
        time.sleep(poll_interval)
    raise RuntimeError("launcher readiness timeout")


def load_json_response(url: str, method: str = "GET") -> tuple[int, dict[str, str], dict[str, Any], int]:
    status, headers, body = http_request(url, method=method, headers={"Accept": "application/json", "Cache-Control": "no-store"})
    payload = json.loads(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected object payload from {url}")
    return status, headers, payload, len(body)


def terminate_process(proc: subprocess.Popen[str]) -> int:
    if proc.poll() is not None:
        return proc.returncode or 0
    try:
        proc.send_signal(signal.SIGINT)
    except ProcessLookupError:
        return proc.returncode or 0
    try:
        return proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            return proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            return proc.wait(timeout=5)
def summarize_stack_probe(status: int, payload: dict[str, Any], payload_size: int) -> dict[str, Any]:
    return {
        "httpStatus": status,
        "payloadSize": payload_size,
        "keyCount": len(payload),
        "categoryCount": int(payload.get("categoryCount", 0)),
        "payloadStatus": str(payload.get("status", "")),
        "bundleMembershipSafe": payload.get("bundleMembershipSafe"),
        "nonAuthoritative": payload.get("nonAuthoritative"),
        "lossModes": payload.get("lossModes", []),
        "safetyGateNote": str(payload.get("safetyGateNote", "")),
    }


def build_stack_probe_url(base_url: str, regime: str, bb: int, position: str, secondary_position: str = "") -> str:
    query_payload = {"regime": regime, "bb": str(bb), "position": position}
    if secondary_position:
        query_payload["secondaryPosition"] = secondary_position
    return f"{base_url}/api/stack?{urlencode(query_payload)}"


def summarize_named_probe(name: str, url: str, status: int, payload: dict[str, Any], payload_size: int) -> dict[str, Any]:
    return {
        "name": name,
        "url": url,
        "httpStatus": status,
        "payloadSize": payload_size,
        "payloadStatus": str(payload.get("status", "")),
        "selectedRegime": str(payload.get("selectedRegime", "")),
        "bb": payload.get("bb"),
        "position": str(payload.get("position", "")),
        "secondaryPosition": str(payload.get("secondaryPosition", "")),
        "categoryCount": int(payload.get("categoryCount", 0)),
        "bundleMembershipSafe": payload.get("bundleMembershipSafe"),
        "nonAuthoritative": payload.get("nonAuthoritative"),
        "comparisonClass": str(payload.get("comparisonClass", "")),
        "exactSemanticsAuthority": str(payload.get("exactSemanticsAuthority", "")),
        "lossModes": payload.get("lossModes", []),
        "lookupKeyTuple": str(payload.get("lookupKeyTuple", "")),
        "safetyGateNote": str(payload.get("safetyGateNote", "")),
    }


def infer_family_from_regime(regime_id: str) -> str:
    if regime_id.startswith("tool10max_"):
        return "push72o_tool_10max_bbante"
    return "jennifear_9max_first_in"


def build_report_markdown(summary: dict[str, Any], http_summary_path: Path) -> str:
    lines = [
        "# consumer reopen on local bridge",
        "",
        f"- sourcePath: {summary['sourcePath']}",
        f"- sourceKind: {summary['sourceKind']}",
        f"- bridgeStartOk: {str(summary['bridgeStartOk']).lower()}",
        f"- bridgeHttpOk: {str(summary['bridgeHttpOk']).lower()}",
        f"- runtimePrivatePackReadable: {str(summary['runtimePrivatePackReadable']).lower()}",
        f"- fullRangeRenderEnabled: {str(summary['fullRangeRenderEnabled']).lower()}",
        f"- statusId: {summary['statusId']}",
        f"- bb1Available: {str(summary['bb1Available']).lower()}",
        f"- bb2to20Available: {str(summary['bb2to20Available']).lower()}",
        f"- bb21to30Available: {str(summary['bb21to30Available']).lower()}",
        f"- uiHttpStatus: {summary['uiHttpStatus']}",
        f"- healthHttpStatus: {summary['healthHttpStatus']}",
        f"- stacksHttpStatus: {summary['stacksHttpStatus']}",
        f"- stack{summary['probeMinBb']}HttpStatus: {summary['stackMinHttpStatus']}",
        f"- stack{summary['probeMinBb']}CategoryCount: {summary['stackMinCategoryCount']}",
        f"- stack{summary['probeMaxBb']}HttpStatus: {summary['stackMaxHttpStatus']}",
        f"- stack{summary['probeMaxBb']}CategoryCount: {summary['stackMaxCategoryCount']}",
        f"- selectedRegime: {summary['selectedRegime']}",
        f"- selectedFamily: {summary['selectedFamily']}",
        f"- availableRegimeCount: {summary['availableRegimeCount']}",
        f"- semanticsActionLabel: {summary['semanticsActionLabel']}",
        f"- semanticsFamilyLabel: {summary['semanticsFamilyLabel']}",
        f"- semanticsLineageLabel: {summary['semanticsLineageLabel']}",
        f"- semanticsTable: {summary['semanticsTable']}",
        f"- semanticsSpot: {summary['semanticsSpot']}",
        f"- semanticsModel: {summary['semanticsModel']}",
        f"- semanticsAnte: {summary['semanticsAnte']}",
        f"- semanticsAnteType: {summary['semanticsAnteType']}",
        f"- semanticsAnteSize: {summary['semanticsAnteSize']}",
        f"- semanticsRangeMode: {summary['semanticsRangeMode']}",
        f"- semanticsSecondaryPositionRole: {summary['semanticsSecondaryPositionRole']}",
        f"- semanticsPositionModeLabel: {summary['semanticsPositionModeLabel']}",
        f"- semanticsSourceName: {summary['semanticsSourceName']}",
        f"- privateNetworkHeaderOnHealth: {str(summary['privateNetworkHeaderOnHealth']).lower()}",
        f"- privateNetworkHeaderOnOptions: {str(summary['privateNetworkHeaderOnOptions']).lower()}",
        f"- probePosition: {summary['probePosition']}",
        f"- probeSecondaryPosition: {summary['probeSecondaryPosition']}",
        f"- launcherLog: {summary['launcherLog']}",
        f"- httpProbeSummary: {http_summary_path.as_posix()}",
    ]
    strict_gate_report = summary.get("strictGateReport")
    if strict_gate_report:
        lines.append(f"- strictGateReport: {strict_gate_report}")
    representative_probes = summary.get("representativeProbes", {})
    if isinstance(representative_probes, dict) and representative_probes:
        lines.append("- representativeProbes:")
        for name, payload in representative_probes.items():
            if not isinstance(payload, dict):
                continue
            lines.append(
                "  - "
                f"{name}: httpStatus={payload.get('httpStatus')} / "
                f"payloadStatus={payload.get('payloadStatus')} / "
                f"categoryCount={payload.get('categoryCount')} / "
                f"bundleMembershipSafe={payload.get('bundleMembershipSafe')} / "
                f"nonAuthoritative={payload.get('nonAuthoritative')} / "
                f"lossModes={payload.get('lossModes')}"
            )
    lines.extend(
        [
            f"- bridgeUiMarkerCount: {summary['bridgeUiMarkerCount']}",
            f"- launcherExitCode: {summary['launcherExitCode']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    launcher_log = out_dir / "launcher.log"
    http_summary_path = out_dir / "http_probe_summary.json"
    summary_path = out_dir / "consumer_reopen_summary.json"
    report_path = out_dir / "consumer_reopen_report.md"

    starter_path = Path(args.starter)
    if not starter_path.exists():
        print(f"ERROR: starter script not found: {starter_path}", file=sys.stderr)
        return 2

    bridge_base = f"http://{args.host}:{args.bridge_port}"
    ui_url = (
        f"http://{args.host}:{args.static_port}/?tab=pushfold-tab"
        f"&pushfoldBridgeBase={quote(bridge_base, safe='')}"
        f"&pushfoldFamily={quote(infer_family_from_regime(args.probe_regime), safe='')}"
        f"&pushfoldRegime={quote(args.probe_regime, safe='')}"
    )
    index_url = f"http://{args.host}:{args.static_port}/index.html"
    health_url = f"{bridge_base}/api/health?{urlencode({'regime': args.probe_regime})}"
    stacks_url = f"{bridge_base}/api/stacks?{urlencode({'regime': args.probe_regime})}"
    stack_min_query_payload = {"regime": args.probe_regime, "bb": str(args.probe_min_bb), "position": args.probe_position}
    stack_max_query_payload = {"regime": args.probe_regime, "bb": str(args.probe_max_bb), "position": args.probe_position}
    if args.probe_secondary_position:
        stack_min_query_payload["secondaryPosition"] = args.probe_secondary_position
        stack_max_query_payload["secondaryPosition"] = args.probe_secondary_position
    stack_min_query = urlencode(stack_min_query_payload)
    stack_max_query = urlencode(stack_max_query_payload)
    stack_min_url = f"{bridge_base}/api/stack?{stack_min_query}"
    stack_max_url = f"{bridge_base}/api/stack?{stack_max_query}"
    representative_probe_results: dict[str, dict[str, Any]] = {}

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
        args.probe_regime,
    ]

    proc: subprocess.Popen[str] | None = None
    try:
        with launcher_log.open("w", encoding="utf-8") as log_file:
            log_file.write(f"starter_cmd={' '.join(starter_cmd)}\n")
            log_file.flush()
            proc = subprocess.Popen(
                starter_cmd,
                cwd=str(REPO_ROOT),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
            )
            wait_until_ready(proc, index_url, health_url, args.health_timeout, args.poll_interval)

        ui_status, _ui_headers, ui_body = http_request(ui_url, headers={"Cache-Control": "no-store"})
        health_status, health_headers, health_payload, health_payload_size = load_json_response(health_url)
        options_status, options_headers, options_body = http_request(health_url, method="OPTIONS")
        stacks_status, _stacks_headers, stacks_payload, stacks_payload_size = load_json_response(stacks_url)
        stack_min_status, _stack_min_headers, stack_min_payload, stack_min_payload_size = load_json_response(stack_min_url)
        stack_max_status, _stack_max_headers, stack_max_payload, stack_max_payload_size = load_json_response(stack_max_url)
        representative_probe_results = {}
        for probe in REPRESENTATIVE_PROBES:
            probe_url = build_stack_probe_url(
                bridge_base,
                probe["regime"],
                probe["bb"],
                probe["position"],
                probe["secondaryPosition"],
            )
            probe_status, _probe_headers, probe_payload, probe_payload_size = load_json_response(probe_url)
            representative_probe_results[probe["name"]] = summarize_named_probe(
                probe["name"],
                probe_url,
                probe_status,
                probe_payload,
                probe_payload_size,
            )
    except Exception as exc:  # noqa: BLE001
        if proc is not None:
            exit_code = terminate_process(proc)
            print(f"launcher_exit_code={exit_code}", file=sys.stderr)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        exit_code = terminate_process(proc) if proc is not None else 1

    ui_text = ui_body.decode("utf-8", errors="replace")
    bridge_ui_markers = {marker: (marker in ui_text) for marker in UI_MARKERS}
    stacks = [int(value) for value in stacks_payload.get("stacks", []) if isinstance(value, int)]
    available_regimes = stacks_payload.get("availableRegimes", []) if isinstance(stacks_payload.get("availableRegimes"), list) else []
    selected_regime = str(stacks_payload.get("selectedRegime", "")).strip()
    semantics_payload = stacks_payload.get("semantics", {}) if isinstance(stacks_payload.get("semantics"), dict) else {}
    expected_2_20 = set(range(2, 21))
    health_private_network = health_headers.get("Access-Control-Allow-Private-Network", "").lower() == "true"
    options_private_network = options_headers.get("Access-Control-Allow-Private-Network", "").lower() == "true"
    bb2to20_available = expected_2_20.issubset(stacks)
    bb21to30_available = any(21 <= value <= 30 for value in stacks)
    probe_stack_bounds_available = args.probe_min_bb in stacks and args.probe_max_bb in stacks
    bridge_start_ok = True
    bridge_http_ok = (
        health_status == 200
        and stacks_status == 200
        and stack_min_status == 200
        and stack_max_status == 200
        and bool(health_payload.get("ok"))
    )
    safe_open_control = representative_probe_results["safeOpenControl"]
    unsafe_open_guard = representative_probe_results["unsafeOpenGuard"]
    safe_call_control = representative_probe_results["safeCallControl"]
    unsafe_call_guard = representative_probe_results["unsafeCallGuard"]
    safe_open_ok = (
        safe_open_control["httpStatus"] == 200
        and safe_open_control["payloadStatus"] == "ok"
        and int(safe_open_control["categoryCount"]) > 0
    )
    unsafe_open_ok = (
        unsafe_open_guard["httpStatus"] == 200
        and unsafe_open_guard["payloadStatus"] == "unsafe_tuple_non_authoritative"
        and unsafe_open_guard["bundleMembershipSafe"] is False
        and unsafe_open_guard["nonAuthoritative"] is True
        and "bundle_missing_membership" in list(unsafe_open_guard["lossModes"])
    )
    safe_call_ok = (
        safe_call_control["httpStatus"] == 200
        and safe_call_control["payloadStatus"] == "ok"
        and int(safe_call_control["categoryCount"]) > 0
    )
    unsafe_call_ok = (
        unsafe_call_guard["httpStatus"] == 200
        and unsafe_call_guard["payloadStatus"] == "unsafe_tuple_non_authoritative"
        and unsafe_call_guard["bundleMembershipSafe"] is False
        and unsafe_call_guard["nonAuthoritative"] is True
        and "bundle_missing_membership" in list(unsafe_call_guard["lossModes"])
        and "dropped_percentage_prefix" in list(unsafe_call_guard["lossModes"])
    )
    bridge_ok = (
        ui_status == 200
        and bridge_http_ok
        and bool(health_payload.get("runtimePrivatePackReadable"))
        and bool(health_payload.get("fullRangeRenderEnabled"))
        and selected_regime == args.probe_regime
        and probe_stack_bounds_available
        and int(stack_min_payload.get("categoryCount", 0)) > 0
        and int(stack_max_payload.get("categoryCount", 0)) > 0
        and health_private_network
        and options_status == 204
        and options_private_network
        and all(bridge_ui_markers.values())
        and safe_open_ok
        and unsafe_open_ok
        and safe_call_ok
        and unsafe_call_ok
    )

    http_summary = {
        "baseUrl": bridge_base,
        "uiUrl": ui_url,
        "sourcePath": SOURCE_PATH,
        "sourceKind": SOURCE_KIND,
        "health": {
            "httpStatus": health_status,
            "payloadSize": health_payload_size,
            "keyCount": len(health_payload),
            "accessControlAllowPrivateNetwork": health_headers.get("Access-Control-Allow-Private-Network", ""),
        },
        "options": {
            "httpStatus": options_status,
            "payloadSize": len(options_body),
            "headerCount": len(options_headers),
            "accessControlAllowPrivateNetwork": options_headers.get("Access-Control-Allow-Private-Network", ""),
        },
        "stacks": {
            "httpStatus": stacks_status,
            "payloadSize": stacks_payload_size,
            "keyCount": len(stacks_payload),
            "stackCount": len(stacks),
            "positionCount": len(stacks_payload.get("positions", [])),
            "minBb": min(stacks) if stacks else None,
            "maxBb": max(stacks) if stacks else None,
            "selectedRegime": selected_regime,
            "availableRegimeCount": len(available_regimes),
            "availableRegimes": available_regimes,
            "semantics": semantics_payload,
            "secondaryPositionsByPosition": stacks_payload.get("secondaryPositionsByPosition", {}),
        },
        "probePosition": args.probe_position,
        "probeSecondaryPosition": args.probe_secondary_position,
        "probeRegime": args.probe_regime,
        "stackProbes": {
            str(args.probe_min_bb): summarize_stack_probe(stack_min_status, stack_min_payload, stack_min_payload_size),
            str(args.probe_max_bb): summarize_stack_probe(stack_max_status, stack_max_payload, stack_max_payload_size),
        },
        "bridgeUiMarkers": bridge_ui_markers,
        "bridgeUiMarkerCount": sum(1 for value in bridge_ui_markers.values() if value),
        "representativeProbes": representative_probe_results,
    }

    summary = {
        "sourcePath": SOURCE_PATH,
        "sourceKind": SOURCE_KIND,
        "bridgeStartOk": bridge_start_ok,
        "bridgeHttpOk": bridge_http_ok,
        "runtimePrivatePackReadable": bool(health_payload.get("runtimePrivatePackReadable")),
        "fullRangeRenderEnabled": bool(health_payload.get("fullRangeRenderEnabled")),
        "statusId": STATUS_ID if bridge_ok else "LOCAL_UI_BRIDGE_CHECK_FAILED",
        "bb1Available": 1 in stacks,
        "bb2to20Available": bb2to20_available,
        "bb21to30Available": bb21to30_available,
        "uiHttpStatus": ui_status,
        "healthHttpStatus": health_status,
        "stacksHttpStatus": stacks_status,
        "probePosition": args.probe_position,
        "probeSecondaryPosition": args.probe_secondary_position,
        "selectedRegime": selected_regime,
        "selectedFamily": str(semantics_payload.get("familyId", "")),
        "availableRegimeCount": len(available_regimes),
        "probeMinBb": args.probe_min_bb,
        "probeMaxBb": args.probe_max_bb,
        "stackMinHttpStatus": stack_min_status,
        "stackMinCategoryCount": int(stack_min_payload.get("categoryCount", 0)),
        "stackMaxHttpStatus": stack_max_status,
        "stackMaxCategoryCount": int(stack_max_payload.get("categoryCount", 0)),
        "semanticsActionLabel": str(semantics_payload.get("actionLabel", "")),
        "semanticsFamilyLabel": str(semantics_payload.get("familyLabel", "")),
        "semanticsLineageLabel": str(semantics_payload.get("lineageLabel", "")),
        "semanticsTable": str(semantics_payload.get("table", "")),
        "semanticsSpot": str(semantics_payload.get("spot", "")),
        "semanticsModel": str(semantics_payload.get("model", "")),
        "semanticsAnte": str(semantics_payload.get("ante", "")),
        "semanticsAnteType": str(semantics_payload.get("anteType", "")),
        "semanticsAnteSize": str(semantics_payload.get("anteSize", "")),
        "semanticsRangeMode": str(semantics_payload.get("rangeMode", "")),
        "semanticsSecondaryPositionRole": str(semantics_payload.get("secondaryPositionRole", "")),
        "semanticsPositionModeLabel": str(semantics_payload.get("positionModeLabel", "")),
        "semanticsSourceName": str(semantics_payload.get("sourceName", "")),
        "privateNetworkHeaderOnHealth": health_private_network,
        "privateNetworkHeaderOnOptions": options_private_network,
        "safeOpenGuardOk": safe_open_ok,
        "unsafeOpenGuardOk": unsafe_open_ok,
        "safeCallGuardOk": safe_call_ok,
        "unsafeCallGuardOk": unsafe_call_ok,
        "representativeProbes": representative_probe_results,
        "bridgeUiMarkerCount": http_summary["bridgeUiMarkerCount"],
        "launcherExitCode": exit_code,
        "launcherLog": launcher_log.as_posix(),
        "strictGateReport": args.strict_gate_report.as_posix() if args.strict_gate_report else None,
    }

    http_summary_path.write_text(json.dumps(http_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(build_report_markdown(summary, http_summary_path) + "\n", encoding="utf-8")

    print(f"status_id={summary['statusId']}")
    print(f"summary={summary_path}")
    print(f"report={report_path}")
    return 0 if bridge_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
