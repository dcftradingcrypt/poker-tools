# HANDOFF_PACKET
version: 14
continuity_protocol_version: 2
kind: canonical_continuity_handoff
scope: startup continuity only
generated_at_utc: 2026-05-12T17:35:00Z
durable_source_rule: repo-root `CLAUDE.md` is the sole durable objective source
continuity_role: startup continuity only
continuity_status: completed
next_exact_action: not_applicable
confirmed_decisions:
  - Use structure-first taxonomy for mix games before collecting open-hand and call-hand range data.
  - Keep exact retained source slices separate from grounded practical heuristic coverage.
  - Do not use blocked-family intake healthchecks as proof after the registry has no blocked families.
  - Use the runtime/static verifier and browser-interaction verifier before claiming browser-facing mix UI confidence.
  - Use the content-source verifier before claiming hand-range/content confidence.
  - Do not treat a public-source asset with zero concrete `source_ref` references as source-lineage verified.
  - Do not treat embedded runtime assets as mirrors unless their payload exactly matches the JSON source artifact.
  - Verify 826's browser-rendered surface text and selectors, not only its static HTML literals, before claiming the public-source boundary is enforced in the UI.
  - Verify every 826 variant/view browser state, not just the default 826 state, before claiming the rendered source-confirmed boundary is enforced.
  - Verify rendered 826 rows against the selected embedded dataset rows, not only boundary text and selector state.
  - Use the aggregate strategy-confidence verifier before claiming the full repo-local mix strategy boundary is verified.
confirmed_repo_state:
  - The current registry boundary grounds all seven structural families: cc_high / 2-card, cc_high / 4-card, cc_hilo / 4-card, stud_high, stud_low_razz, stud_hilo, and draw_triple_low.
  - The mix-game display lane intentionally exposes six non-AoF structural families; cc_high / 2-card remains in the Push/Fold lane.
  - cc_high / 4-card and cc_hilo / 4-card are exact retained-source slices, not full-family solved corpora.
  - stud_high, stud_low_razz, stud_hilo, and draw_triple_low are grounded practical heuristic coverage, not exact charts or solver outputs.
  - PLO8, Badugi, A-5 Triple Draw, Stud8, and 826 UI surfaces include public-source or practical display assets where present, but those surfaces must not be confused with structural-family exactness claims.
  - 826 is source-confirmed archetype/risk guidance only; public sources do not support an exact UTG/HJ/CO/BTN/SB range matrix or exact BB defense matrix.
completed_items:
  - Repaired stale blocked-family continuity state after the registry moved to no blocked families.
  - Added current-strategy verification for grounded-family boundary, display classification, UI synthesis alignment, source-backed asset presence, and stale continuity regressions.
  - Added runtime/static mix UI verification for Node syntax checks, embedded asset mirrors, and optional headless Chrome DOM/screenshot smoke.
  - Added headless Chrome interaction verification for all visible mix-game surfaces through the live game selector, expected per-game controls, and runtime/console error capture.
  - Fixed the exact-spot loader retry loop so same-page error states do not recursively re-render unless explicitly refreshed.
  - Added content-source verification for visible mix-game hand-range numbers, public-source asset lineage, and obvious broken Japanese copy fragments.
  - Downgraded 826 from position-specific hand ranges to public-source-confirmed archetypes and risk overlays.
  - Added 826 `source_coverage` references so its public archetype/risk asset has concrete source lineage instead of a vacuous zero-ref pass.
  - Extended content-source verification to reject zero-ref lineage, obvious broken public copy fragments, and mojibake signatures in public mix surfaces.
  - Extended runtime/static verification to require embedded JS payloads to exactly match their JSON source artifacts.
  - Extended 826 content checks to reject old `open_raise` / `bb_defense_call` view keys, non-`SOURCE_CONFIRMED` pseudo-position keys, empty public rows, missing source coverage, and missing source-boundary coverage.
  - Extended browser-interaction verification so the rendered 826 surface must include boundary text, use only archetype/risk views, expose only `SOURCE_CONFIRMED` scope, and omit old Open / BB Call labels.
  - Extended browser-interaction verification to walk every 826 variant/view combination (`FL826TD` and `NL826SD`, `archetypes` and `risk_overlays`) and re-check boundary text, non-empty rendered surface, selector sync, and `SOURCE_CONFIRMED` scope after each switch.
  - Extended browser-interaction verification to compare each selected 826 `SOURCE_CONFIRMED` row from the embedded runtime dataset against the rendered surface text.
  - Tightened 826 source-coverage verification so extra covered views and empty coverage entries fail instead of being silently accepted.
  - Added aggregate verifier `scripts/verify_mix_game_strategy_confidence.py` so content, strategy, runtime, browser, and blocked-family boundary checks can be run from one command.
  - Marked the aggregate blocked-family toolchain healthcheck inactive when no blocked families remain, so a vacuous zero-subtest pass cannot be treated as strategy evidence.
required_repo_evidence: []
required_user_decisions: []
required_user_steps: []
blocking_reason: not_applicable
completion_reason: The current mix-game grounding/display strategy has a repo-local verifier and no current user-owned blocked step.
invalid_reasons: []
notes:
  - Use `python -B scripts/verify_mix_game_grounding_strategy.py` for the current strategy confidence check.
  - Use `python -B scripts/verify_mix_game_content_sources.py` for hand-range/source-alignment and Japanese-copy sanity checks.
  - Use `python -B scripts/verify_mix_game_runtime_static.py --browser-exe "C:\Program Files\Google\Chrome\Application\chrome.exe"` for browser-facing mix UI confidence on this machine.
  - Use `python -B scripts/verify_mix_game_browser_interactions.py --browser-exe "C:\Program Files\Google\Chrome\Application\chrome.exe"` for all-visible-game switching, per-game sub-control, and runtime-error confidence on this machine.
  - Use `python -B scripts/verify_mix_game_strategy_confidence.py --browser-exe "C:\Program Files\Google\Chrome\Application\chrome.exe" --require-browser` as the aggregate confidence gate for the current repo-local strategy boundary.
  - Use blocked-family intake scripts only if a future registry reintroduces blocked families or a new family-source promotion lane is explicitly opened.
