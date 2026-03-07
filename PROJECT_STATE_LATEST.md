# PROJECT STATE LATEST

- acceptance_latest: `out/_codex/run_20260306-062913_warn_id_diff_and_acceptance_update/acceptance_receipt.md`
- consumer_status_latest: `out/_codex/run_20260308-041231_consumer_reopen_on_local_bridge/consumer_reopen_report.md`
- acceptanceStatusId: `ACCEPTED_2_20_KNOWN_WARN_ONLY`
- consumerStatusId: `FOUND_LOCAL_UI_BRIDGE_CONSUMER`
- currentDefault: acceptance は有効、consumer は local bridge 経由で利用可能、21–30 は source missing
- reopenConditions:
  - `real_consumer_repo_url`
  - `real_consumer_release_artifact_or_binary`
  - `local_executable_consumer_cli_or_module_path`
  - `official_docs_or_readme_with_real_consumer_command`
- note: acceptance 系と consumer 系は別固定参照で管理する
