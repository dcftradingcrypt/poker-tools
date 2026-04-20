# Overview Spec: Three-Actor Runtime Contract

## Purpose
Define the current intended behavior for the User / GPT / Codex runtime contract artifacts.

## Boundaries
This overview governs only the source contract artifacts under repair:
- PROMPT_PACK.md
- AGENTS.override.md
- .agents/skills/handoff-packet/SKILL.md
- .agents/skills/handoff-packet/agents/openai.yaml

Generated continuity outputs are not source authority for prompt semantics.

## Inputs / Outputs
Inputs:
- current user request
- GPT-visible chat-readable sources
- active CODEX_TASK relay
- repo-local sources named by active CODEX_TASK and AGENTS.override.md

Outputs:
- GPT_DIRECT response
- CODEX_TASK relay
- USER_ACTION_REQUIRED
- repo-side edits and verification outputs from Codex
- canonical continuity outputs only through continuity_refresh

## State model / invariants
- actor authority remains partitioned across User / GPT / Codex
- PROMPT_PACK.md is GPT-only and not Codex-readable
- Codex acts only through an active CODEX_TASK
- USER_ACTION_REQUIRED exists only for user-owned next steps
- continuity refresh route, source selection, and execution must agree exactly

## Ordering / timing rules
Route must be evaluated end-to-end from user intent through GPT routing to Codex execution and resulting output.

## Error handling
Only execution-changing defects are release-blocking.
Separate:
- real execution-changing defects
- duplicate manifestations
- wording / documentation issues

## Compatibility notes / assumptions
This work assumes PROMPT_PACK.md is attached to the GPT project and readable by GPT, but not by Codex.

## Tests / regression cases
Required checks:
- mixed-intent requests (resume + explicit task)
- continuity refresh source selection cases
- normal repo work writable-target cases
- decision reply consumption cases
- deferred follow-up cases

## Open issues
To be filled by current worklog and decision log entries.
