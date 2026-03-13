[Max仕様]
MODE: MAX
SCOPE: short
VERIFICATION: standard

第一読取点は repo ルートの `HANDOFF_PACKET.md`。
`PROJECT_STATE_LATEST.md` / `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md` / `REAL_CONSUMER_STATUS_LATEST.md` は `HANDOFF_PACKET.md` から辿る補助 pointer であり、先読みしない。
repo root 正本の bootstrap 名は `NEW_CHAT_BOOTSTRAP.md`。run-local mirror は `out/_codex/run_20260313-183536_unified_publish_remote_parity/handoff/NEW_CHAT_BOOTSTRAP.txt` で、内容は byte-identical を維持する。
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
- `out/_codex/run_20260313-044416_aof_dedicated_view/page_boundary_report.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/runtime_root_cause_report.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/before_after_dom.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/audit_packet.md`

現時点の既定状態:
- `acceptanceStatusId=ACCEPTED_2_20_KNOWN_WARN_ONLY`
- `consumerStatusId=FOUND_LOCAL_UI_BRIDGE_CONSUMER`
- same-page `winrate-tab` fix `ui-status-fix-20260310-064557@333f7fa0e6881b8cf3d7b4931f047fd1662e11bf` は historical baseline で、remote read-only verification `PASS`
- historical fix scope は `index.html` 1 file only で、slot 移動 / `8765` bridge-base 維持 / `winrate-tab` 再初期化が確定
- `HANDOFF_PACKET.md` / `NEW_CHAT_BOOTSTRAP.md` / `scripts/start_pushfold_local.py` は fix commit では no-diff
- current code closure は `run_20260313-044416_aof_dedicated_view`
- before は `working=served=reference=dbb6cbe2ed552f81cbdd9453cbebaf3f770f9970` で、same-page codepath
- after は dedicated tab `pushfold-tab` を追加し、`working=served=75abb40192909e6325718b49e4e04f57532a1c53`
- AOF は `AOF` タブ側だけに表示され、target online=`full` / target offline=`fallback` / non-target=`hidden`
- `bb2to20Available=true`、`bb21to30Available=false` を current state として維持し、21-30bb は frozen
- unified publish remote parity canonical artifact は `run_20260313-183536_unified_publish_remote_parity` で、remote branch `unified-publish-dedicated-view-20260313-061735@237180afe404f789b335cc88e1fcf898fde7bf28` は `index.html` / `HANDOFF_PACKET.md` / `NEW_CHAT_BOOTSTRAP.md` の 3 files only scope で `PASS`
- local 起動は `scripts/start_pushfold_local.py` を優先し、durability の direct proof は `run_20260310-024514_handoff_refresh` を使う
- broken baseline `handoff-push-only-20260310-052252@5719a38b1263ff0f6a0eafea2c2f8e93c03a8a6f` は comparison only、外部WRITEは未実施

runtime detail が必要なら `out/_codex/run_20260313-044416_aof_dedicated_view/page_boundary_report.md`、`runtime_root_cause_report.md`、`before_after_dom.md` を先に読む。

range 本文、TSV 本文、response payload、一致行、機密情報は展開禁止。
