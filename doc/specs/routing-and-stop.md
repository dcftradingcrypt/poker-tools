# Spec: Routing and Stop Behavior

## Purpose
Define exact end-to-end routing and stop behavior for the current step.

## Boundaries
Applies from user request interpretation through GPT routing to final stop or relay.

## Inputs / Outputs
Inputs:
- current user request
- active carried state allowed by source contracts
- discovery sources allowed by source contracts

Outputs:
- one selected current-step task
- or one USER_ACTION_REQUIRED
- or one GPT_DIRECT response
- or one CODEX_TASK relay

## State model / invariants
- A current step must resolve to exactly one next action.
- Resume intent must not erase an explicitly selected current-step task.
- Control utterances must not be treated as executable work items.
- Deferred follow-up items must have an exact retrieval path if they are meant to persist to the next step.

## Ordering / timing rules
1. interpret current user request
2. determine selected current-step task if present
3. otherwise continue open work if exactly one next item exists
4. otherwise perform allowed discovery
5. only then emit a user-owned stop if required

## Error handling
Do not guess task order when more than one item exists without an exact current-step selector.

## Compatibility notes / assumptions
Mixed-intent user messages are allowed and must route deterministically.

## Tests / regression cases
- resume-only utterance
- explicit-task-only request
- resume + explicit task in same message
- deferred follow-up after completing the first selected task
- decision reply consuming a prior numbered decision

## Open issues
Need exact source-level rules for decision reply consumption and deferred follow-up retrieval.
