#!/usr/bin/env python3
"""Static and optional headless-browser runtime checks for the mix UI.

The grounding-strategy verifier proves the repo artifacts agree with each
other. This script checks the browser-facing layer more directly:

- external and inline JavaScript parse with Node,
- embedded runtime mirror assets are syntactically valid window assignments to
  non-empty JSON payloads,
- optionally, a headless Chromium-family browser can load the mix tab, render a
  DOM with the expected controls, and capture a nonblank screenshot.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import zlib
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


RUNTIME_CHECK_VERSION = "1.2"
EXPECTED_MIX_DOM_MARKERS = [
    'id="mix-display-surface"',
    'id="mix-game-select"',
    "PLO High",
    "Badugi",
    "Stud8",
    "826",
]
EMBEDDED_JSON_MIRRORS = {
    "assets/pushfold/aof-bundle.embedded.v1.js": "assets/pushfold/aof-bundle.v1.json",
    "assets/pushfold/aof-bundle-safety.embedded.v1.js": "assets/pushfold/aof-bundle-safety.v1.json",
    "assets/mix/badugi-pre-draw-public-ranges.embedded.v1.js": "assets/mix/badugi-pre-draw-public-ranges.v1.json",
    "assets/mix/a5-triple-draw-public-ranges.embedded.v1.js": "assets/mix/a5-triple-draw-public-ranges.v1.json",
    "assets/mix/stud8-third-street-public-ranges.embedded.v1.js": "assets/mix/stud8-third-street-public-ranges.v1.json",
    "assets/mix/basil-826-public-ranges.embedded.v1.js": "assets/mix/basil-826-public-ranges.v1.json",
    "assets/mix/deuce-to-seven-triple-draw-public-ranges.embedded.v1.js": "assets/mix/deuce-to-seven-triple-draw-public-ranges.v1.json",
    "assets/mix/plo-high-preflop-public-ranges.embedded.v1.js": "assets/mix/plo-high-preflop-public-ranges.v1.json",
    "assets/mix/plo8-preflop-public-ranges.embedded.v1.js": "assets/mix/plo8-preflop-public-ranges.v1.json",
    "assets/mix/razz-third-street-public-ranges.embedded.v1.js": "assets/mix/razz-third-street-public-ranges.v1.json",
    "assets/mix/stud-high-third-street-public-ranges.embedded.v1.js": "assets/mix/stud-high-third-street-public-ranges.v1.json",
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


def add_check(checks: list[CheckResult], check_id: str, ok: bool, detail: str) -> None:
    checks.append(CheckResult(check_id, "passed" if ok else "failed", detail))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_scripts(index_html: str) -> tuple[list[str], list[str]]:
    external: list[str] = []
    inline: list[str] = []
    script_pattern = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.I | re.S)
    for match in script_pattern.finditer(index_html):
        attrs = match.group("attrs") or ""
        body = match.group("body") or ""
        src_match = re.search(r'\bsrc="([^"]+)"', attrs, re.I)
        if src_match:
            external.append(src_match.group(1))
            continue
        type_match = re.search(r'\btype="([^"]+)"', attrs, re.I)
        script_type = type_match.group(1).strip().lower() if type_match else ""
        if script_type and script_type not in {"text/javascript", "application/javascript", "module"}:
            continue
        if body.strip():
            inline.append(body)
    return external, inline


def run_command(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def verify_node_syntax(checks: list[CheckResult], root: Path, external_scripts: list[str], inline_scripts: list[str]) -> None:
    node = shutil.which("node")
    add_check(checks, "node.available", bool(node), f"node executable={node or ''}")
    if not node:
        return
    version = run_command([node, "--version"], root, timeout=10)
    add_check(
        checks,
        "node.version",
        version.returncode == 0 and version.stdout.strip().startswith("v"),
        f"node version stdout={version.stdout.strip()} stderr={version.stderr.strip()}",
    )

    for rel_path in external_scripts:
        if not rel_path.endswith(".js"):
            continue
        script_path = root / rel_path
        if not script_path.is_file():
            add_check(checks, f"node.external.{rel_path}", False, "external script is missing")
            continue
        completed = run_command([node, "--check", str(script_path)], root, timeout=120)
        add_check(
            checks,
            f"node.external.{rel_path}",
            completed.returncode == 0,
            f"node --check return={completed.returncode} stderr={completed.stderr.strip()[:300]}",
        )

    with tempfile.TemporaryDirectory(prefix="popker_mix_inline_") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        for index, body in enumerate(inline_scripts, start=1):
            temp_path = temp_dir / f"inline_script_{index}.js"
            temp_path.write_text(body, encoding="utf-8")
            completed = run_command([node, "--check", str(temp_path)], root, timeout=120)
            add_check(
                checks,
                f"node.inline.{index}",
                completed.returncode == 0,
                f"node --check return={completed.returncode} stderr={completed.stderr.strip()[:300]}",
            )


def verify_embedded_assets(checks: list[CheckResult], root: Path, external_scripts: list[str]) -> None:
    embedded_scripts = [path for path in external_scripts if path.endswith(".embedded.v1.js")]
    missing_mirrors_from_page = [
        rel_path for rel_path in EMBEDDED_JSON_MIRRORS
        if rel_path not in external_scripts
    ]
    add_check(
        checks,
        "embedded_asset.all_json_mirrors_loaded_by_page",
        not missing_mirrors_from_page,
        f"missingFromIndex={missing_mirrors_from_page}",
    )
    add_check(
        checks,
        "embedded_asset.count",
        len(embedded_scripts) >= 7,
        f"embedded script count={len(embedded_scripts)} scripts={embedded_scripts}",
    )
    assignment_pattern = re.compile(r"^\s*window\.([A-Za-z0-9_]+)\s*=\s*(.*);\s*$", re.S)
    for rel_path in embedded_scripts:
        script_path = root / rel_path
        if not script_path.is_file():
            add_check(checks, f"embedded_asset.{rel_path}.exists", False, "missing embedded asset")
            continue
        body = read_text(script_path)
        match = assignment_pattern.match(body)
        if not match:
            add_check(
                checks,
                f"embedded_asset.{rel_path}.assignment",
                False,
                "embedded asset must be a single window.__NAME = JSON assignment",
            )
            continue
        global_name, json_text = match.group(1), match.group(2)
        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError as exc:
            add_check(checks, f"embedded_asset.{rel_path}.json", False, f"JSON parse failed: {exc}")
            continue
        non_empty = bool(payload) if isinstance(payload, (dict, list)) else payload is not None
        add_check(
            checks,
            f"embedded_asset.{rel_path}.json",
            non_empty and global_name.startswith("__"),
            f"global={global_name} type={type(payload).__name__} nonEmpty={non_empty}",
        )


def verify_embedded_asset_mirrors(checks: list[CheckResult], root: Path, external_scripts: list[str]) -> None:
    assignment_pattern = re.compile(r"^\s*window\.([A-Za-z0-9_]+)\s*=\s*(.*);\s*$", re.S)
    checked = 0
    for embedded_rel_path, json_rel_path in EMBEDDED_JSON_MIRRORS.items():
        checked += 1
        embedded_path = root / embedded_rel_path
        json_path = root / json_rel_path
        if not embedded_path.is_file() or not json_path.is_file():
            add_check(
                checks,
                f"embedded_mirror.{embedded_rel_path}",
                False,
                f"missing mirror input embedded={embedded_path.is_file()} json={json_path.is_file()}",
            )
            continue
        match = assignment_pattern.match(read_text(embedded_path))
        if not match:
            add_check(
                checks,
                f"embedded_mirror.{embedded_rel_path}",
                False,
                "embedded asset is not a single window assignment",
            )
            continue
        try:
            embedded_payload = json.loads(match.group(2))
            json_payload = json.loads(read_text(json_path))
        except json.JSONDecodeError as exc:
            add_check(
                checks,
                f"embedded_mirror.{embedded_rel_path}",
                False,
                f"JSON parse failed: {exc}",
            )
            continue
        add_check(
            checks,
            f"embedded_mirror.{embedded_rel_path}",
            embedded_payload == json_payload,
            f"embedded payload must exactly match {json_rel_path}",
        )
    add_check(
        checks,
        "embedded_mirror.coverage",
        checked == len(EMBEDDED_JSON_MIRRORS),
        f"mirrors checked={checked} expected={len(EMBEDDED_JSON_MIRRORS)}",
    )


def serve_repo(root: Path) -> tuple[ThreadingHTTPServer, str]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            rel_url = urllib.parse.unquote(parsed.path)
            rel_path = "index.html" if rel_url in {"", "/"} else rel_url.lstrip("/")
            candidate = (root / rel_path).resolve()
            if not (candidate == (root / "index.html").resolve() or str(candidate).startswith(str(root.resolve()) + os.sep)):
                self.send_error(404)
                return
            if not candidate.is_file():
                self.send_error(404)
                return
            content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            if candidate.suffix == ".js":
                content_type = "application/javascript"
            elif candidate.suffix == ".json":
                content_type = "application/json"
            elif candidate.suffix == ".html":
                content_type = "text/html"
            data = candidate.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def paeth(left: int, up: int, up_left: int) -> int:
    estimate = left + up - up_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    up_left_distance = abs(estimate - up_left)
    if left_distance <= up_distance and left_distance <= up_left_distance:
        return left
    if up_distance <= up_left_distance:
        return up
    return up_left


def decode_png_rgb_samples(path: Path, max_rows: int = 120) -> tuple[int, int, int, int]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a png")
    pos = 8
    width = height = bit_depth = color_type = 0
    idat_parts: list[bytes] = []
    while pos < len(data):
        length = int.from_bytes(data[pos : pos + 4], "big")
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if chunk_type == b"IHDR":
            width = int.from_bytes(chunk_data[0:4], "big")
            height = int.from_bytes(chunk_data[4:8], "big")
            bit_depth = chunk_data[8]
            color_type = chunk_data[9]
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break
    if bit_depth != 8 or color_type not in {2, 6}:
        raise ValueError(f"unsupported png bit_depth={bit_depth} color_type={color_type}")
    channels = 3 if color_type == 2 else 4
    stride = width * channels
    raw = zlib.decompress(b"".join(idat_parts))
    previous = bytearray(stride)
    unique: set[tuple[int, int, int]] = set()
    nonwhite = 0
    sampled = 0
    row_limit = min(height, max_rows)
    for row_index in range(row_limit):
        offset = row_index * (stride + 1)
        filter_type = raw[offset]
        scanline = bytearray(raw[offset + 1 : offset + 1 + stride])
        for i in range(stride):
            left = scanline[i - channels] if i >= channels else 0
            up = previous[i]
            up_left = previous[i - channels] if i >= channels else 0
            if filter_type == 1:
                scanline[i] = (scanline[i] + left) & 0xFF
            elif filter_type == 2:
                scanline[i] = (scanline[i] + up) & 0xFF
            elif filter_type == 3:
                scanline[i] = (scanline[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                scanline[i] = (scanline[i] + paeth(left, up, up_left)) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"unsupported png filter={filter_type}")
        previous = scanline
        step = channels * 8
        for i in range(0, stride, step):
            rgb = (scanline[i], scanline[i + 1], scanline[i + 2])
            unique.add(rgb)
            sampled += 1
            if rgb != (255, 255, 255):
                nonwhite += 1
    return width, height, len(unique), nonwhite if sampled else 0


def verify_browser_smoke(checks: list[CheckResult], root: Path, browser_exe: str | None) -> None:
    if not browser_exe:
        add_check(
            checks,
            "browser.smoke.skipped",
            True,
            "no --browser-exe supplied; run with a Chromium-family browser for DOM/screenshot smoke",
        )
        return
    browser_path = Path(browser_exe)
    add_check(checks, "browser.executable_exists", browser_path.is_file(), str(browser_path))
    if not browser_path.is_file():
        return

    server, base_url = serve_repo(root)
    try:
        with tempfile.TemporaryDirectory(prefix="popker_mix_browser_") as temp_dir_raw:
            temp_dir = Path(temp_dir_raw)
            user_data_dir = temp_dir / "profile"
            screenshot_path = temp_dir / "mix-smoke.png"
            url = f"{base_url}/?tab=mix-tab"
            common_args = [
                str(browser_path),
                "--headless=new",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-background-networking",
                "--no-first-run",
                "--no-default-browser-check",
                "--hide-scrollbars",
                "--window-size=1280,900",
                "--virtual-time-budget=8000",
                f"--user-data-dir={user_data_dir}",
            ]
            dom_args = common_args + [
                "--dump-dom",
                url,
            ]
            completed = run_command(dom_args, root, timeout=45)
            dom = completed.stdout or ""
            stderr = completed.stderr or ""
            marker_misses = [marker for marker in EXPECTED_MIX_DOM_MARKERS if marker not in dom]
            add_check(
                checks,
                "browser.dump_dom",
                completed.returncode == 0 and not marker_misses,
                (
                    f"return={completed.returncode} url={url} domLength={len(dom)} "
                    f"missingMarkers={marker_misses} stderr={stderr.strip()[:300]}"
                ),
            )
            screenshot_args = common_args + [
                f"--screenshot={screenshot_path}",
                url,
            ]
            screenshot_completed = run_command(screenshot_args, root, timeout=45)
            screenshot_ok = screenshot_path.is_file() and screenshot_path.stat().st_size > 10_000
            try:
                width, height, unique_count, nonwhite_count = decode_png_rgb_samples(screenshot_path)
            except Exception as exc:  # noqa: BLE001
                width = height = unique_count = nonwhite_count = 0
                screenshot_ok = False
                screenshot_detail = f"decode failed: {exc}"
            else:
                screenshot_detail = (
                    f"size={screenshot_path.stat().st_size} width={width} height={height} "
                    f"uniqueSampleColors={unique_count} nonwhiteSamples={nonwhite_count} "
                    f"return={screenshot_completed.returncode} stderr={screenshot_completed.stderr.strip()[:300]}"
                )
            add_check(
                checks,
                "browser.screenshot_nonblank",
                screenshot_completed.returncode == 0
                and screenshot_ok
                and width == 1280
                and height == 900
                and unique_count > 16
                and nonwhite_count > 100,
                screenshot_detail,
            )
    finally:
        server.shutdown()
        server.server_close()
        time.sleep(0.1)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    checks: list[CheckResult] = []
    index_path = root / "index.html"
    add_check(checks, "input.index_html.exists", index_path.is_file(), "index.html must exist")
    index_html = read_text(index_path) if index_path.is_file() else ""
    external_scripts, inline_scripts = extract_scripts(index_html)
    add_check(
        checks,
        "input.script_tags",
        len(external_scripts) >= 7 and len(inline_scripts) >= 1,
        f"externalScripts={len(external_scripts)} inlineScripts={len(inline_scripts)}",
    )
    verify_node_syntax(checks, root, external_scripts, inline_scripts)
    verify_embedded_assets(checks, root, external_scripts)
    verify_embedded_asset_mirrors(checks, root, external_scripts)
    verify_browser_smoke(checks, root, args.browser_exe)
    failed = [check for check in checks if check.status != "passed"]
    payload = {
        "runtimeCheckVersion": RUNTIME_CHECK_VERSION,
        "repoRoot": ".",
        "status": "passed" if not failed else "failed",
        "summary": {
            "checksTotal": len(checks),
            "checksPassed": len(checks) - len(failed),
            "checksFailed": len(failed),
            "failedCheckIds": [check.check_id for check in failed],
            "browserSmokeExecuted": bool(args.browser_exe),
        },
        "checks": [check.as_dict() for check in checks] if args.verbose or failed else [],
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-exe", default="", help="Optional Chromium-family browser executable.")
    parser.add_argument("--verbose", action="store_true", help="Include all checks in output.")
    return parser.parse_args()


def main() -> int:
    payload = build_payload(parse_args())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
