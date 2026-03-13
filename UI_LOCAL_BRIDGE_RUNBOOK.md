# UI LOCAL BRIDGE RUNBOOK

- start: `python3 scripts/private_pack_ui_server.py --host 127.0.0.1 --port 8765`
- bind: `127.0.0.1` only
- fallback: bridge unavailable の場合は availability-only UI に留め、full range render は無効
- data handling: rangeString / TSV / response body を repo/public/out/_codex に保存しない
