#!/usr/bin/env python3
"""Aggregate confidence check for the current mix-game strategy boundary.

This does not prove poker EV optimality. It makes the repo-local confidence
claim harder to misuse by running the content, strategy, runtime, browser, and
blocked-family boundary verifiers from one entrypoint.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


AGGREGATE_CHECK_VERSION = "1.0"


@dataclass
class RunResult:
    check_id: str
    status: str
    command: list[str]
    detail: str
    parsed_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "checkId": self.check_id,
            "status": self.status,
            "command": self.command,
            "detail": self.detail,
            "parsedStatus": self.parsed_status,
        }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_json_command(check_id: str, command: list[str], root: Path, allowed_statuses: set[str]) -> RunResult:
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=240,
    )
    parsed_status = ""
    detail = ""
    ok = completed.returncode == 0
    try:
        payload = json.loads(completed.stdout)
        parsed_status = str(payload.get("status", ""))
        summary = payload.get("summary", {})
        detail = json.dumps(summary, ensure_ascii=False, sort_keys=True)
        ok = ok and parsed_status in allowed_statuses
    except json.JSONDecodeError:
        detail = f"non-json stdout={completed.stdout[:500]!r} stderr={completed.stderr[:500]!r}"
        ok = False
    if completed.stderr.strip():
        detail = f"{detail}; stderr={completed.stderr.strip()[:500]}"
    return RunResult(
        check_id=check_id,
        status="passed" if ok else "failed",
        command=command,
        detail=detail,
        parsed_status=parsed_status,
    )


def build_commands(args: argparse.Namespace, root: Path) -> list[tuple[str, list[str], set[str]]]:
    python = sys.executable
    commands: list[tuple[str, list[str], set[str]]] = [
        (
            "content_sources",
            [python, "-B", str(root / "scripts/verify_mix_game_content_sources.py")],
            {"passed"},
        ),
        (
            "grounding_strategy",
            [python, "-B", str(root / "scripts/verify_mix_game_grounding_strategy.py")],
            {"passed"},
        ),
        (
            "runtime_static",
            [python, "-B", str(root / "scripts/verify_mix_game_runtime_static.py")],
            {"passed"},
        ),
        (
            "blocked_family_health",
            [python, "-B", str(root / "scripts/verify_mix_game_blocked_family_toolchain_health.py")],
            {"passed", "inactive_no_blocked_families"},
        ),
    ]
    if args.browser_exe:
        commands.append(
            (
                "runtime_static_browser",
                [
                    python,
                    "-B",
                    str(root / "scripts/verify_mix_game_runtime_static.py"),
                    "--browser-exe",
                    args.browser_exe,
                ],
                {"passed"},
            )
        )
        commands.append(
            (
                "browser_interactions",
                [
                    python,
                    "-B",
                    str(root / "scripts/verify_mix_game_browser_interactions.py"),
                    "--browser-exe",
                    args.browser_exe,
                ],
                {"passed"},
            )
        )
    elif args.require_browser:
        commands.append(("browser_interactions", [], {"passed"}))
    return commands


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    results: list[RunResult] = []
    for check_id, command, allowed_statuses in build_commands(args, root):
        if not command:
            results.append(
                RunResult(
                    check_id=check_id,
                    status="failed",
                    command=[],
                    detail="--require-browser was supplied but --browser-exe is missing",
                    parsed_status="",
                )
            )
            continue
        results.append(run_json_command(check_id, command, root, allowed_statuses))

    failed = [result for result in results if result.status != "passed"]
    browser_executed = bool(args.browser_exe)
    return {
        "aggregateCheckVersion": AGGREGATE_CHECK_VERSION,
        "repoRoot": str(root),
        "status": "passed" if not failed else "failed",
        "summary": {
            "checksTotal": len(results),
            "checksPassed": len(results) - len(failed),
            "checksFailed": len(failed),
            "failedCheckIds": [result.check_id for result in failed],
            "browserExecuted": browser_executed,
            "boundedConfidenceClaim": (
                "repo-local mix strategy boundary is verified"
                if not failed and browser_executed
                else "repo-local mix strategy boundary is only partially verified"
                if not failed
                else "repo-local mix strategy boundary is not verified"
            ),
        },
        "checks": [result.as_dict() for result in results] if args.verbose or failed else [],
        "residualRisk": [
            "Aggregate pass does not prove poker EV or solver optimality.",
            "Aggregate pass does not validate non-public or paywalled 826 exact thresholds.",
            "External public pages can change after repo-local source notes are captured.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-exe", default="", help="Chromium-family browser executable for browser checks.")
    parser.add_argument("--require-browser", action="store_true", help="fail if --browser-exe is not provided.")
    parser.add_argument("--verbose", action="store_true", help="include individual command results")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    payload = build_payload(parse_args(argv))
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
