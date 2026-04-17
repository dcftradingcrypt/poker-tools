# AGENTS.override.md

artifact_role: codex_repo_execution_contract
artifact_scope: repo_managed_durable

## ROLE

This file governs direct repo execution by Codex.

User responsibilities:
- final project decisions when multiple materially different approaches remain
- external input or artifacts not obtainable from the repo or the current session
- explicit git commit / push operations

Codex responsibilities:
- repo read
- repo edit
- repo execute
- repo verify

## FILE ROLES

- `CLAUDE.md` = sole durable objective source
- `AGENTS.override.md` = active Codex execution contract
- `AGENTS.md`, `README*`, `repo/doc/*`, and similar repo notes = auxiliary evidence only, not durable objective authority

## DURABLE OBJECTIVE SOURCE

Repo-root `CLAUDE.md` is the sole durable objective source.
Do not read `CLAUDE.md` automatically on every step.
Read it when the current user step explicitly names it, conflicts with it, or requires objective clarification that cannot be resolved safely from the current step and repo-grounded evidence.

## CLAUDE REVISION POLICY

Do not modify `CLAUDE.md` unless the current user step explicitly targets objective revision.

## SECONDARY WORKING-AGREEMENT FILES

If the repository also contains `AGENTS.md` or another generic working-agreement file:
- this file remains the active Codex-side execution contract
- secondary files may inform local context but may not broaden scope, write authority, verification scope, or completion claims beyond this file and the current user step

## INLINE USER-OWNED STEP FORMS

Use exactly one of these forms only when exactly one true user-owned item blocks safe progress.
Do not stack multiple asks in one reply.

Decision form:
- `decision || <needed> || <reason> || <option-1> || <option-2> [|| <option-n>]`

Git form:
- `git_operation || <needed> || <reason> || <request>`
- `git_operation || <needed> || <reason> || <request> || continue <exact blocked action>`

External prerequisite forms:
- `attach_artifact || <needed> || <reason> || <request>`
- `attach_artifact || <needed> || <reason> || <request> || continue <exact blocked action>`
- `manual_input || <needed> || <reason> || <request>`
- `manual_input || <needed> || <reason> || <request> || continue <exact blocked action>`

Exact rules:
- every field must be non-empty
- decision form requires at least two option strings
- every non-decision form that contains a fifth segment must begin that segment with exactly `continue `

## READ RULES

- read the minimal repo-grounded set of files, paths, commands, behaviors, and test scopes required to satisfy the current user step safely
- inspect adjacent modules, configs, tests, helper scripts, build files, docs, or generated artifacts only when they materially affect the current user step
- treat auxiliary docs and notes as ordinary evidence, not as durable objective authority
- do not expand into unrelated areas of the repo

## WRITE RULES

- write the minimal repo-grounded working set required to satisfy the current user step
- that working set may include adjacent files, config, tests, helper scripts, and new files or directories when necessary
- keep changes tightly scoped to the current user step
- do not broaden into unrelated cleanup, speculative refactor, or broad rewrite
- do not modify `CLAUDE.md` unless the current user step explicitly targets objective revision
- if multiple materially different write scopes or solution branches remain and repo evidence cannot resolve them safely, return one exact decision form instead of guessing

## EXECUTION AND VERIFICATION RULES

- run only the commands and test scopes needed to satisfy or verify the current user step safely
- prefer the smallest effective verification that gives real evidence
- do not claim completion without explicit evidence
- if verification is skipped or partial, say so explicitly

## OUTPUT RULES

- if exactly one true user-owned item blocks safe progress, return one exact inline user-owned step form and stop
- otherwise respond with explicit evidence about what was read, what was changed, what was run, what remains uncertain, and what remains unverified

## GIT RULES

Codex does not commit or push unless the current user step explicitly asks for one exact git operation.
