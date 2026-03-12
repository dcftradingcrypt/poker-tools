# HANDOFF_PACKET

## メタ
- MODE: MAX
- SCOPE: short
- VERIFICATION: standard
- 第一読取点: `HANDOFF_PACKET.md`
- root 同期対象: `HANDOFF_PACKET.md`, `NEW_CHAT_BOOTSTRAP.md`
- bootstrap 命名マッピング: repo root 正本は `NEW_CHAT_BOOTSTRAP.md`、run-local mirror は `out/_codex/run_20260313-061735_unified_publish_sync/handoff/NEW_CHAT_BOOTSTRAP.txt`。内容は byte-identical を維持する。
- 根拠範囲: `HANDOFF_PACKET.md` を起点に、補助 pointer 文書と指定 run summary の existence / short-status を参照する。

## 目的
- 次チャットが貼り付け無しで再開できるよう、`HANDOFF_PACKET.md` を project 再開の第一読取点に固定する。
- fixed refs / acceptance 系 / consumer status 本文は変更せず、補助 pointer として handoff から辿れる状態に保つ。

## 補助ポインタ（この handoff 読後のみ参照）
- `PROJECT_STATE_LATEST.md`
  - `acceptance_latest`: `out/_codex/run_20260306-062913_warn_id_diff_and_acceptance_update/acceptance_receipt.md`
  - `consumer_status_latest`: `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_report.md`
  - `acceptanceStatusId`: `ACCEPTED_2_20_KNOWN_WARN_ONLY`
  - `consumerStatusId`: `FOUND_LOCAL_UI_BRIDGE_CONSUMER`
- `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`
  - `latest_receipt`: `out/_codex/run_20260306-062913_warn_id_diff_and_acceptance_update/acceptance_receipt.md`
- `REAL_CONSUMER_STATUS_LATEST.md`
  - `latest_consumer_status`: `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_report.md`

## 確定状態
1. acceptance は継続有効。
- 2-20bb は `ACCEPTED_2_20_KNOWN_WARN_ONLY` のまま維持。
- 21-30bb は source missing の扱いを維持し、推測補完しない。

2. consumer は local UI bridge が正本。
- `FOUND_LOCAL_UI_BRIDGE_CONSUMER` を維持。
- `consumer_reopen_summary.json` では `bridgeStartOk=true`, `bridgeHttpOk=true`, `bb2to20Available=true`, `bb21to30Available=false`, `dangerAllZero=true`。

3. `333f7fa` same-page fix は historical baseline として保持し、current code closure は dedicated view を正本にする。
- `out/_codex/run_20260311-012940_ui_status_fix/ui_status_anchor_report.md` と `ui_status_update_report.md` では remote PASS fix の scope が `index.html` 1 file only、slot 移動、`8765` bridge-base 維持、`winrate-tab` 再初期化であることが確定している。
- ただし same-page `winrate-tab` path は current closure ではない。`run_20260313-044416_aof_dedicated_view` が `pushfold-tab` 専用 view を current code closure として採用する。

4. local launcher durability は direct proof で再確認済み。
- `out/_codex/run_20260310-024514_handoff_refresh/http_probe_summary.json` では `index.html` の bridge-base literal が `http://127.0.0.1:8765`、`bb2to20Available=true`、`bb21to30Available=false`、`stack21` は `404/stack_unavailable`。
- `out/_codex/run_20260310-024514_handoff_refresh/dom_launch_smoke.json` では offline target が `fallback`、offline non-target が `hidden`、online target が `full` かつ `appliedCategoryCount=11`、online non-target が `hidden`。
- `out/_codex/run_20260310-024514_handoff_refresh/launcher_stdout.txt` では launcher が `ui_url http://127.0.0.1:8766/?tab=winrate-tab` と `bridge_health_url http://127.0.0.1:8765/api/health` を emit。

5. remote read-only verification は PASS。
- `out/_codex/run_20260311-182657_remote_readonly_verification/remote_verification_report.md` では `ui-status-fix-20260310-064557@333f7fa0e6881b8cf3d7b4931f047fd1662e11bf` の remote read-only verification が `PASS`。
- broken baseline `handoff-push-only-20260310-052252@5719a38b1263ff0f6a0eafea2c2f8e93c03a8a6f` は comparison only として扱う。
- `out/_codex/run_20260311-182657_remote_readonly_verification/audit_packet.md` では GitHub commit `333f7fa` が parent `5719a38...`, `index.html` 1 file only, `+19/-8` と記録されている。
- `out/_codex/run_20260311-182657_remote_readonly_verification/no_diff_decision.md` では fix commit に対して `HANDOFF_PACKET.md` / `NEW_CHAT_BOOTSTRAP.md` / `scripts/start_pushfold_local.py` が no-diff。
- 外部WRITE は今回も未実施。

6. current code closure は `run_20260313-044416_aof_dedicated_view` を採用。
- before は `working=served=reference=dbb6cbe2ed552f81cbdd9453cbebaf3f770f9970`。
- before 実装は verified reference そのもので、`#pushfold-surface-slot` が `winrate-tab` 配下にある same-page codepath だった。
- after は dedicated tab `pushfold-tab` を追加し、`working=served=75abb40192909e6325718b49e4e04f57532a1c53`。
- AOF は `AOF` タブ側だけに表示され、`対想定レンジ` 側からは外れた。
- target online は `full`、target offline は `fallback`、non-target は `hidden`。
- `bb2to20Available=true`、`bb21to30Available=false` を current state として維持し、21-30bb は frozen。
- `out/_codex/run_20260313-044416_aof_dedicated_view/summary_key_check.json` では `allPresent=true`、`leak_counts_only.json` では `dangerAllZero=true`。

## 次チャットの既定手順
1. 第一読取点は repo root の `HANDOFF_PACKET.md`。
2. 次に repo root の `NEW_CHAT_BOOTSTRAP.md` を読む。run-local mirror が必要なら `out/_codex/run_20260313-061735_unified_publish_sync/handoff/NEW_CHAT_BOOTSTRAP.txt` を使ってよいが、内容は root と同一であることを前提にする。
3. その後 `PROJECT_STATE_LATEST.md`、`HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`、`REAL_CONSUMER_STATUS_LATEST.md` を補助 pointer として読む。
4. local runtime の再検証が要る場合は `out/_codex/run_20260313-044416_aof_dedicated_view/page_boundary_report.md`、`runtime_root_cause_report.md`、`before_after_dom.md` を第一証拠にし、必要なら `out/_codex/run_20260310-024514_handoff_refresh/launcher_durability_report.md` と `scripts/start_pushfold_local.py` を補助起点にする。
5. 2-20bb available / 21-30 unavailable を維持し、新証拠が無い限り 21-30 を補完しない。
6. remote 側の再確認が必要なら `out/_codex/run_20260311-182657_remote_readonly_verification/remote_verification_report.md` を第一証拠にし、broken baseline `handoff-push-only-20260310-052252@5719a38...` は比較用としてのみ扱う。新規変更が無い限り外部WRITEは行わない。

## 参照対象
- `out/_codex/run_20260306-062913_warn_id_diff_and_acceptance_update/acceptance_receipt.md`
- `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_summary.json`
- `out/_codex/run_20260309-022311_ui_scope_fix/ui_scope_summary.json`
- `out/_codex/run_20260310-024514_handoff_refresh/http_probe_summary.json`
- `out/_codex/run_20260310-024514_handoff_refresh/dom_launch_smoke.json`
- `out/_codex/run_20260311-012940_ui_status_fix/ui_status_anchor_report.md`
- `out/_codex/run_20260311-012940_ui_status_fix/ui_status_update_report.md`
- `out/_codex/run_20260311-012940_ui_status_fix/before_after_dom.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/remote_verification_report.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/no_diff_decision.md`
- `out/_codex/run_20260311-182657_remote_readonly_verification/audit_packet.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/page_boundary_report.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/runtime_root_cause_report.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/before_after_dom.md`
- `out/_codex/run_20260313-044416_aof_dedicated_view/summary_key_check.json`
- `out/_codex/run_20260313-044416_aof_dedicated_view/leak_counts_only.json`
- `out/_codex/run_20260313-044416_aof_dedicated_view/audit_packet.md`
- `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`
- `REAL_CONSUMER_STATUS_LATEST.md`
- `PROJECT_STATE_LATEST.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `CLAUDE.md`

## 禁止
- range 本文、TSV 本文、response payload、一致行、機密値は保存しない。
- push / PR 作成 / merge などの外部WRITEは実行しない。
