[Max仕様]
MODE: MAX
SCOPE: short
VERIFICATION: standard

第一読取点は repo ルートの `HANDOFF_PACKET.md`。
`PROJECT_STATE_LATEST.md` / `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md` / `REAL_CONSUMER_STATUS_LATEST.md` は `HANDOFF_PACKET.md` から辿る補助 pointer であり、先読みしない。
repo root 正本の bootstrap 名は `NEW_CHAT_BOOTSTRAP.md`。run-local mirror は `out/_codex/run_20260310-013948_handoff/handoff/NEW_CHAT_BOOTSTRAP.txt` で、内容は byte-identical を維持する。
`HANDOFF_PACKET.md` 読後、必要時のみ以下の補助証拠を辿れ。
- `PROJECT_STATE_LATEST.md`
- `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`
- `REAL_CONSUMER_STATUS_LATEST.md`
- `out/_codex/run_20260310-024514_handoff_refresh/launcher_durability_report.md`
- `out/_codex/run_20260310-024514_handoff_refresh/http_probe_summary.json`
- `out/_codex/run_20260310-024514_handoff_refresh/dom_launch_smoke.json`
- `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_summary.json`
- `out/_codex/run_20260309-022311_ui_scope_fix/ui_scope_summary.json`
- `out/_codex/run_20260309-034428_ui_scope_fix_checkpoint_and_packet_refresh/push_ready_packet.json`
- `out/_codex/run_20260309-064316_post_push_remote_probe/remote_probe_summary.json`
- `out/_codex/run_20260309-183754_pushfold_local_launch_fix/launch_fix_summary.json`

現時点の既定状態:
- `acceptanceStatusId=ACCEPTED_2_20_KNOWN_WARN_ONLY`
- `consumerStatusId=FOUND_LOCAL_UI_BRIDGE_CONSUMER`
- push/fold UI は `winrate-tab` 限定、`bb2to20Available=true`、`bb21to30Available=false`
- local 起動は `scripts/start_pushfold_local.py` を優先し、durability の direct proof は `run_20260310-024514_handoff_refresh` を使う
- remote main には local head `5dfa668c3537930899237f524597122e47c7e44d` が未反映、外部WRITEは未実施

range 本文、TSV 本文、response payload、一致行、機密情報は展開禁止。
