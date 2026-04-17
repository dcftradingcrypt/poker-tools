# NEW_CHAT_BOOTSTRAP

## Startup input rule
- continuity-aware startup requires the GPT-attached `PROMPT_PACK.md` visible to that GPT in the current chat
- use attached `HANDOFF_PACKET.md` as continuity state
- use attached `NEW_CHAT_BOOTSTRAP.md` as startup companion and continuity-status cross-check only

## Durable source rule
- treat `CLAUDE.md` as sole durable objective source for explicit objective-check tasks only

## Continuity status
- `continuity_status: blocked_user_step`

## Startup rule
1. name the handoff artifact in use
2. restate only non-empty carried-state fields among `confirmed_decisions`, `confirmed_repo_state`, `completed_items`, `required_repo_evidence`, `required_user_decisions`, `required_user_steps`, `blocking_reason`, `completion_reason`, `invalid_reasons`, and `notes`
3. state continuity_status
4. if the current user request contains one selected current-step task, follow that current user request first
5. else if continuity_status = ready_to_resume, continue `next_exact_action`
6. else if continuity_status = blocked_user_decision, emit one exact `USER_ACTION_REQUIRED` from `required_user_decisions`
7. else if continuity_status = blocked_missing_evidence, emit one exact `CODEX_TASK` derived from `required_repo_evidence`
8. else if continuity_status = blocked_user_step, emit one exact `USER_ACTION_REQUIRED` from `required_user_steps`
9. else if continuity_status = completed, acknowledge that no resumable carried work remains and wait for one explicit next instruction
10. else if continuity_status = invalid_packet, stop and request continuity repair or one explicit new instruction
11. do not perform next-work discovery during continuity-aware startup
12. do not use `CLAUDE.md` as startup fallback

## Notes
- startup continuity only
- not durable objective authority
