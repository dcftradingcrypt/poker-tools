#!/usr/bin/env python3
import argparse
import json
import signal
import sys
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import private_pack_ui_server as bridge_server


REPO_ROOT = Path(__file__).resolve().parents[1]


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def copyfile(self, source, outputfile) -> None:
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--static-port", type=int, default=8766)
    parser.add_argument("--bridge-port", type=int, default=8765)
    parser.add_argument("--health-timeout", type=float, default=15.0)
    parser.add_argument("--poll-interval", type=float, default=0.25)
    parser.add_argument("--pack", default=str(REPO_ROOT / "out/_private/pushfold_real_data/pack.json"))
    parser.add_argument("--regimes-root", default=str(REPO_ROOT / "out/_private/pushfold_real_data_regimes"))
    parser.add_argument("--index", default=str(REPO_ROOT / "index.html"))
    parser.add_argument("--pushfold-regime", default="antes0")
    return parser


def probe_http_ok(url: str, timeout: float = 1.0) -> bool:
    request = Request(url, headers={"Cache-Control": "no-store"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 0) < 400
    except (HTTPError, URLError, TimeoutError):
        return False


def wait_until_ready(url: str, timeout: float, poll_interval: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if probe_http_ok(url):
            return
        time.sleep(poll_interval)
    raise RuntimeError(f"health_timeout {url}")


def serve_forever(server: ThreadingHTTPServer) -> None:
    server.serve_forever(poll_interval=0.25)


def build_static_server(host: str, port: int) -> ThreadingHTTPServer:
    handler = partial(QuietStaticHandler, directory=str(REPO_ROOT))
    return ThreadingHTTPServer((host, port), handler)


def build_bridge_server(host: str, port: int, pack_path: str, regimes_root: str, index_path: str) -> ThreadingHTTPServer:
    app_state = bridge_server.build_app_state(pack_path, regimes_root)
    server = ThreadingHTTPServer((host, port), bridge_server.PrivatePackUiHandler)
    server.app = {  # type: ignore[attr-defined]
        "index": index_path,
        **app_state,
    }
    return server


def stop_server(server: ThreadingHTTPServer) -> None:
    server.shutdown()
    server.server_close()


def main() -> int:
    args = build_parser().parse_args()
    static_server = build_static_server(args.host, args.static_port)
    bridge_http_server = build_bridge_server(args.host, args.bridge_port, args.pack, args.regimes_root, args.index)
    app_state = bridge_http_server.app  # type: ignore[attr-defined]
    selected_regime_entry = app_state.get("regimes", {}).get(args.pushfold_regime, {})
    selected_family = str(selected_regime_entry.get("semantics", {}).get("familyId", "")).strip()
    static_thread = Thread(target=serve_forever, args=(static_server,), daemon=True)
    bridge_thread = Thread(target=serve_forever, args=(bridge_http_server,), daemon=True)
    stop_requested = False

    def request_stop(*_args) -> None:
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    static_thread.start()
    bridge_thread.start()

    static_root = f"http://{args.host}:{args.static_port}"
    bridge_root = f"http://{args.host}:{args.bridge_port}"
    pushfold_query = urlencode({
        "tab": "pushfold-tab",
        "pushfoldBridgeBase": bridge_root,
        "pushfoldFamily": selected_family,
        "pushfoldRegime": args.pushfold_regime,
    })
    ui_url = f"{static_root}/?{pushfold_query}"
    non_target_query = urlencode({
        "tab": "evcalc-tab",
        "pushfoldBridgeBase": bridge_root,
        "pushfoldFamily": selected_family,
        "pushfoldRegime": args.pushfold_regime,
    })
    ui_non_target_url = f"{static_root}/?{non_target_query}"
    health_query = urlencode({"regime": args.pushfold_regime})
    bridge_health_url = f"{bridge_root}/api/health?{health_query}"
    try:
        wait_until_ready(f"{static_root}/index.html", args.health_timeout, args.poll_interval)
        wait_until_ready(bridge_health_url, args.health_timeout, args.poll_interval)
        print("pushfold_local_ready", flush=True)
        print(f"ui_url {ui_url}", flush=True)
        print(f"ui_non_target_url {ui_non_target_url}", flush=True)
        print(
            f"pushfold_runtime_query {json.dumps({'pushfoldBridgeBase': bridge_root, 'pushfoldFamily': selected_family, 'pushfoldRegime': args.pushfold_regime}, ensure_ascii=False)}",
            flush=True,
        )
        print(f"bridge_health_url {bridge_health_url}", flush=True)
        print("press_ctrl_c_to_stop", flush=True)
        while not stop_requested:
            time.sleep(0.5)
    except RuntimeError as err:
        print(str(err), file=sys.stderr, flush=True)
        return 1
    finally:
        stop_server(bridge_http_server)
        stop_server(static_server)
        bridge_thread.join(timeout=5)
        static_thread.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
