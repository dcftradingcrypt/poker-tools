# Spec: Normal Repo Work

## Purpose
Define how normal repo work reads, writes, and verifies repo-local targets.

## Boundaries
Applies to workflow_type = normal_repo_work.

## Inputs / Outputs
Inputs:
- active CODEX_TASK for normal_repo_work
- repo-local files/paths named in scope
- repo-root CLAUDE.md as readable higher-authority source if allowed by contract

Outputs:
- repo edits or verification results inside the authorized writable set

## State model / invariants
- Normal repo work must have an exact writable-target rule.
- The contract must define whether only the goal-named target is writable or whether broader scope paths can be writable.
- Scope-named targets not in the writable set are read-only for the current task.
- CLAUDE.md readability does not automatically widen writable scope.

## Ordering / timing rules
- establish goal
- establish scope
- establish writable target set
- execute only within that read/write boundary

## Error handling
If writable authorization is ambiguous, do not execute.

## Compatibility notes / assumptions
This spec should align exactly between PROMPT_PACK.md and AGENTS.override.md.

## Tests / regression cases
- read-only repo inspection
- single-file edit
- attempt to edit a scope-only target not authorized for write
- CLAUDE.md present but unrelated cleanup not authorized

## Open issues
Need exact source wording for writable-target semantics and CLAUDE.md scope interaction.
