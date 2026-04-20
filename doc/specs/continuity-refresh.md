# Spec: Continuity Refresh

## Purpose
Define continuity refresh routing, source selection, execution, and outputs.

## Boundaries
Applies only to workflow_type = continuity_refresh.

## Inputs / Outputs
Inputs:
- selected current-step task requesting canonical continuity refresh
- exact supported continuity source selector
- attached continuity artifacts or canonical repo-root pair as permitted

Outputs:
- canonical HANDOFF_PACKET.md and NEW_CHAT_BOOTSTRAP.md pair
- or exact user-owned stop when source decision or missing user-supplied artifacts are required

## State model / invariants
- Route gate and execution capability must match.
- Unsupported continuity source forms must be rejected or redirected explicitly.
- Silent fallback between source modes is not allowed.
- Generated continuity outputs are never semantic authority for prompt behavior.

## Ordering / timing rules
1. determine whether the current step explicitly requests continuity refresh
2. determine supported source selector
3. if selector is unsupported or conflicted, emit exact user-owned stop
4. otherwise route exactly one continuity_refresh CODEX_TASK
5. execute only within the continuity generation contract

## Error handling
- missing attached artifacts for an explicitly requested attached-pair source -> USER_ACTION_REQUIRED(attach_artifact)
- source decision ambiguity -> USER_ACTION_REQUIRED(decision)
- lane-local contract defect -> GPT-owned correction, not user escalation

## Compatibility notes / assumptions
Canonical pair refresh is the supported output shape unless and until source files explicitly add a supported single-file mode.

## Tests / regression cases
- attached explicit pair source
- canonical repo-root pair source
- unsupported single-file source request
- conflicted attached + repo-root request
- absent repo-root pair when explicitly requested

## Open issues
Need confirmation that no supported single-file continuity refresh route should exist in source semantics.
