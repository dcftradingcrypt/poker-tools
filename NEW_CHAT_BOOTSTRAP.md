[Max仕様]
MODE: MAX
SCOPE: short
VERIFICATION: standard

第一読取点は repo ルートの `HANDOFF_PACKET.md`。
`PROJECT_STATE_LATEST.md` / `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md` / `REAL_CONSUMER_STATUS_LATEST.md` は `HANDOFF_PACKET.md` から辿る補助 pointer であり、先読みしない。
repo root 正本の bootstrap 名は `NEW_CHAT_BOOTSTRAP.md`。run-local mirror は `out/_codex/run_20260312-000434_handoff_pass_sync/handoff/NEW_CHAT_BOOTSTRAP.txt` で、内容は byte-identical を維持する。
`HANDOFF_PACKET.md` 読後、必要時のみ以下の補助証拠を辿れ。
- `PROJECT_STATE_LATEST.md`
- `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`
- `REAL_CONSUMER_STATUS_LATEST.md`
- `out/_codex/run_20260310-024514_handoff_refresh/launcher_durability_report.md`
- `out/_codex/run_20260310-024514_handoff_refresh/http_probe_summary.json`
- `out/_codex/run_20260310-024514_handoff_refresh/dom_launch_smoke.json`
- `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_summary.json`
- `out/_codex/run_20260309-022311_ui_scope_fix/ui_scope_summary.json`
- `out/_codex/run_20260311-012940_ui_status_fix/ui_status_anchor_report.md`
- `out/_codex/run_20260311-012940_ui_status_fix/ui_status_update_report.md`
- `out/_codex/run_20260311-012940_ui_status_fix/before_after_dom.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/remote_verification_report.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/no_diff_decision.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/audit_packet.md`

現時点の既定状態:
- `acceptanceStatusId=ACCEPTED_2_20_KNOWN_WARN_ONLY`
- `consumerStatusId=FOUND_LOCAL_UI_BRIDGE_CONSUMER`
- push/fold UI は `winrate-tab` 限定で、fix commit `ui-status-fix-20260310-064557@333f7fa0e6881b8cf3d7b4931f047fd1662e11bf` は remote read-only verification `PASS`
- fix scope は `index.html` 1 file only で、slot 移動 / `8765` bridge-base 維持 / `winrate-tab` 再初期化が確定
- `HANDOFF_PACKET.md` / `NEW_CHAT_BOOTSTRAP.md` / `scripts/start_pushfold_local.py` は fix commit では no-diff
- `bb2to20Available=true`、`bb21to30Available=false` を current state として維持し、21-30bb は frozen
- local 起動は `scripts/start_pushfold_local.py` を優先し、durability の direct proof は `run_20260310-024514_handoff_refresh` を使う
- broken baseline `handoff-push-only-20260310-052252@5719a38b1263ff0f6a0eafea2c2f8e93c03a8a6f` は comparison only、外部WRITEは未実施

range 本文、TSV 本文、response payload、一致行、機密情報は展開禁止。
