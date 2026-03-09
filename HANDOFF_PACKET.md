# HANDOFF_PACKET

## メタ
- MODE: MAX
- SCOPE: short
- VERIFICATION: standard
- 第一読取点: `HANDOFF_PACKET.md`
- root 同期対象: `HANDOFF_PACKET.md`, `NEW_CHAT_BOOTSTRAP.md`
- bootstrap 命名マッピング: repo root 正本は `NEW_CHAT_BOOTSTRAP.md`、run-local mirror は `out/_codex/run_20260310-013948_handoff/handoff/NEW_CHAT_BOOTSTRAP.txt`。内容は byte-identical を維持する。
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

3. UI scope fix は反映済み。
- `ui_scope_summary.json` では push/fold は `winrate-tab` のみ表示、`evcalc-tab` では非表示。
- online target は `fullRangeRenderEnabledOnTarget=true`、offline target は fallback のみ。

4. local launcher durability は direct proof で再確認済み。
- `out/_codex/run_20260310-024514_handoff_refresh/http_probe_summary.json` では `index.html` の bridge-base literal が `http://127.0.0.1:8765`、`bb2to20Available=true`、`bb21to30Available=false`、`stack21` は `404/stack_unavailable`。
- `out/_codex/run_20260310-024514_handoff_refresh/dom_launch_smoke.json` では offline target が `fallback`、offline non-target が `hidden`、online target が `full` かつ `appliedCategoryCount=11`、online non-target が `hidden`。
- `out/_codex/run_20260310-024514_handoff_refresh/launcher_stdout.txt` では launcher が `ui_url http://127.0.0.1:8766/?tab=winrate-tab` と `bridge_health_url http://127.0.0.1:8765/api/health` を emit。

5. remote 反映は未完了。
- `remote_probe_summary.json` では `pushObserved=false`, `status=FAIL_REMOTE_NOT_REFLECTED`, `localAheadCountVsOriginMain=5`, `openPrCount=0`。
- `git ls-remote --heads --tags origin` では `refs/heads/main=eebba674d336de96cd0e094dc095c3ff03536072` と `refs/heads/gpt-5=7b78adfa939f6422c586042e1e46b8ab6994762e` のみで、local head `5dfa668c3537930899237f524597122e47c7e44d` は remote ref に未反映。
- 外部WRITE は未実施のまま維持し、必要時は runbook を使う。

## 次チャットの既定手順
1. 第一読取点は repo root の `HANDOFF_PACKET.md`。
2. 次に repo root の `NEW_CHAT_BOOTSTRAP.md` を読む。run-local mirror が必要なら `out/_codex/run_20260310-013948_handoff/handoff/NEW_CHAT_BOOTSTRAP.txt` を使ってよいが、内容は root と同一であることを前提にする。
3. その後 `PROJECT_STATE_LATEST.md`、`HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`、`REAL_CONSUMER_STATUS_LATEST.md` を補助 pointer として読む。
4. local runtime の再検証が要る場合は `out/_codex/run_20260310-024514_handoff_refresh/launcher_durability_report.md` と `scripts/start_pushfold_local.py` を起点にする。
5. 2-20bb available / 21-30 unavailable を維持し、新証拠が無い限り 21-30 を補完しない。
6. remote branch/PR が既に無い限り外部WRITEは行わず、runbook に従って人手で push/PR を実施する。

## 参照対象
- `out/_codex/run_20260306-062913_warn_id_diff_and_acceptance_update/acceptance_receipt.md`
- `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_summary.json`
- `out/_codex/run_20260309-022311_ui_scope_fix/ui_scope_summary.json`
- `out/_codex/run_20260309-034428_ui_scope_fix_checkpoint_and_packet_refresh/push_ready_packet.json`
- `out/_codex/run_20260309-064316_post_push_remote_probe/remote_probe_summary.json`
- `out/_codex/run_20260309-183754_pushfold_local_launch_fix/launch_fix_summary.json`
- `HANDOFF_ACCEPTANCE_RECEIPT_LATEST.md`
- `REAL_CONSUMER_STATUS_LATEST.md`
- `PROJECT_STATE_LATEST.md`
- `NEW_CHAT_BOOTSTRAP.md`
- `CLAUDE.md`

## 禁止
- range 本文、TSV 本文、response payload、一致行、機密値は保存しない。
- push / PR 作成 / merge などの外部WRITEは実行しない。
