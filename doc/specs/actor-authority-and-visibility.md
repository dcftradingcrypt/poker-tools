# Spec: Actor Authority and Visibility

## Purpose
Define exact actor responsibilities and visibility boundaries.

## Boundaries
Applies to User, GPT, and Codex responsibilities across the source contract artifacts.

## Inputs / Outputs
Inputs:
- current user request
- GPT-visible chat-readable sources
- active CODEX_TASK relay
- repo-local sources permitted by AGENTS.override.md

Outputs:
- GPT_DIRECT
- CODEX_TASK
- USER_ACTION_REQUIRED
- Codex execution results

## State model / invariants
- User owns decisions, input supply, relay, and git actions.
- GPT owns routing, startup interpretation, audit, review, and user-facing orchestration.
- Codex owns repo-local read/edit/execute/verify only inside active CODEX_TASK scope.
- PROMPT_PACK.md is GPT-only.
- Codex does not directly read PROMPT_PACK.md.
- Generated continuity files are not semantic authority for prompt behavior.

## Ordering / timing rules
- GPT performs routing before any Codex execution.
- Codex acts only after one active CODEX_TASK exists.

## Error handling
- User-owned next step -> USER_ACTION_REQUIRED
- Lane-local defect -> GPT_DIRECT or corrected relay, not user escalation unless truly user-owned

## Compatibility notes / assumptions
PROMPT_PACK.md may be attached to the GPT project and readable by GPT in the current chat without becoming Codex-readable.

## Tests / regression cases
- GPT-only PROMPT_PACK.md does not leak into Codex-readable set
- no direct user -> Codex execution lane
- user relay does not transfer routing authority

## Open issues
Need to verify exact wording in the source files matches these invariants.
