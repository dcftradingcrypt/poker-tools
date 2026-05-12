# HANDOFF_PACKET
version: 6
continuity_protocol_version: 2
kind: canonical_continuity_handoff
scope: startup continuity only
generated_at_utc: 2026-04-11T16:30:18Z
durable_source_rule: repo-root `CLAUDE.md` is the sole durable objective source
continuity_role: startup continuity only
continuity_status: blocked_user_step
next_exact_action: not_applicable
confirmed_decisions:
  - Use structure-first taxonomy for mix games before collecting open-hand and call-hand range data.
  - Use structure-first taxonomy for mix games before collecting family-specific data for open/call modeling.
confirmed_repo_state:
  - Existing repo-grounded range artifact is currently limited to No-Limit Hold'em push/fold and does not yet cover a true mixed-game rotation.
  - Existing repo-grounded range artifact remains limited to cc_high / 2-card No-Limit Hold'em push/fold; cc_high / 4-card, cc_hilo / 4-card, stud_high, stud_low_razz, stud_hilo, and draw_triple_low remain blocked_no_source pending exact family-native source lineage.
  - The blocked-family intake toolchain is operational end to end, including family registry, candidate validation, batch validation, staging, promotion review, one-shot intake entrypoint, retained-source seeding, source-drop workflow, and aggregate toolchain healthcheck.
completed_items:
  - Repaired the governing continuity contract in .agents/skills/handoff-packet/SKILL.md so pair agreement now checks continuity_status only.
  - Created provisional artifact out/_codex/poker_mix_open_call_ranges.md limited to No-Limit Hold'em push/fold (10max / BB ante 100%).
  - Built aligned family taxonomy, source inventory, grounding gates, and acquisition plan for the six blocked families.
  - Built blocked-family ingest contracts, non-grounding pack and manifest templates, machine-readable family contract registry, single-candidate validator, batch validator, staging lane, promotion review lane, one-shot intake entrypoint, retained-source seeding lane, source-drop workflow, and aggregate toolchain healthcheck.
  - Verified grounded cc_high / 2-card runtime and bundle guard coverage and confirmed no remaining active runtime_user_facing_risk_bearing consumer in scope.
required_repo_evidence: []
required_user_decisions: []
required_user_steps:
  - attach_artifact || blocked-family source-drop files || blocked-family promotion cannot proceed because the intake and review toolchain is complete but no provenance-complete blocked-family candidate exists in repo scope || attach one retained blocked-family source file set or one candidate pack/manifest pair for exactly one of cc_high / 4-card, cc_hilo / 4-card, stud_high, stud_low_razz, stud_hilo, or draw_triple_low || continue run the source-drop workflow and promotion review for the supplied family
blocking_reason: No real provenance-complete blocked-family candidate exists in repo scope, so promotion_candidate_pending_human_review cannot be exercised honestly.
completion_reason: not_applicable
invalid_reasons: []
notes:
  - Current poker workstream is to classify mix games by structural family first, then collect family-specific data for open/call modeling.
  - Current next useful operational lane after refresh is user-supplied blocked-family source-drop intake through scripts/run_mix_game_source_drop_workflow.py.
  - The stale taxonomy-drafting next_exact_action in the current continuity pair must be removed or replaced during refresh.
