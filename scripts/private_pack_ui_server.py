#!/usr/bin/env python3
import argparse
import json
import re
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


RANKS = "AKQJT98765432"
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
    parser.add_argument(
        "--pack",
        default=str(Path(__file__).resolve().parents[1] / "out/_private/pushfold_real_data/pack.json"),
    )
    parser.add_argument(
        "--index",
        default=str(Path(__file__).resolve().parents[1] / "index.html"),
    )
    return parser


@lru_cache(maxsize=1)
def load_pack(pack_path: str) -> dict:
    return json.loads(Path(pack_path).read_text(encoding="utf-8"))


def parse_categories(raw_value: str) -> list[str]:
    seen = set()
    categories = []
    for token in re.findall(r"\b[2-9TJQKA]{2}(?:s|o)?\b", raw_value or ""):
        if token in VALID_CATEGORIES and token not in seen:
            seen.add(token)
            categories.append(token)
    return categories


def build_catalog(pack: dict) -> dict:
    stacks = [int(x) for x in pack.get("stacksBb", []) if isinstance(x, (int, float))]
    positions = [str(x) for x in pack.get("positions", []) if isinstance(x, str)]
    ranges = pack.get("ranges", {}) if isinstance(pack, dict) else {}
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
    return {
        "stacks": stacks,
        "positions": positions,
        "catalog": catalog,
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
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.serve_index()
            return
        if parsed.path == "/api/health":
            self.serve_json(self.health_payload())
            return
        if parsed.path == "/api/stacks":
            self.serve_json(self.stacks_payload())
            return
        if parsed.path == "/api/stack":
            self.serve_stack_payload(parse_qs(parsed.query))
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
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def health_payload(self) -> dict:
        stacks = self.app["stacks"]
        positions = self.app["positions"]
        return {
            "ok": True,
            "runtimePrivatePackReadable": True,
            "fullRangeRenderEnabled": True,
            "stackCount": len(stacks),
            "minBb": min(stacks) if stacks else None,
            "maxBb": max(stacks) if stacks else None,
            "positionCount": len(positions),
        }

    def stacks_payload(self) -> dict:
        return {
            "ok": True,
            "runtimePrivatePackReadable": True,
            "fullRangeRenderEnabled": True,
            "stacks": self.app["stacks"],
            "positions": self.app["positions"],
        }

    def serve_stack_payload(self, query: dict) -> None:
        bb_raw = (query.get("bb") or [""])[0]
        position = (query.get("position") or [""])[0]
        if not re.fullmatch(r"\d+", bb_raw):
            self.serve_json({"ok": False, "status": "invalid_bb"}, HTTPStatus.BAD_REQUEST)
            return
        bb = int(bb_raw)
        stack_map = self.app["catalog"].get(bb)
        if not stack_map:
            self.serve_json({"ok": False, "status": "stack_unavailable", "bb": bb}, HTTPStatus.NOT_FOUND)
            return
        if position not in stack_map:
            self.serve_json(
                {"ok": False, "status": "position_unavailable", "bb": bb, "position": position},
                HTTPStatus.NOT_FOUND,
            )
            return
        categories = stack_map[position]
        self.serve_json(
            {
                "ok": True,
                "status": "ok",
                "bb": bb,
                "position": position,
                "categoryCount": len(categories),
                "categories": categories,
            }
        )


def main() -> int:
    args = build_parser().parse_args()
    pack = load_pack(args.pack)
    catalog = build_catalog(pack)
    server = ThreadingHTTPServer((args.host, args.port), PrivatePackUiHandler)
    server.app = {  # type: ignore[attr-defined]
        "index": args.index,
        "stacks": catalog["stacks"],
        "positions": catalog["positions"],
        "catalog": catalog["catalog"],
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
