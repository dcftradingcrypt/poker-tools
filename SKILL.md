---
name: repo-runtime
description: Execute the current user step directly in this repository under AGENTS.override.md using the minimal repo-grounded working set required to satisfy it safely.
---

# Mission

Execute the current user step directly in this repository.

This skill performs repo work.
It does not build wrappers for another execution layer.

# Contract precedence

1. `AGENTS.override.md`
2. this skill

If this file and `AGENTS.override.md` disagree, follow `AGENTS.override.md`.

# Operating model

1. Identify the current user step.
2. Read `AGENTS.override.md`.
3. Read `CLAUDE.md` only when objective clarification is required under `AGENTS.override.md`.
4. Inspect the minimal repo-grounded working set needed to do the step safely.
5. Edit the minimal repo-grounded working set needed to satisfy the step.
6. Run the minimal commands or tests needed to verify the result.
7. If exactly one true user-owned item blocks safe progress, return one exact inline user-owned step form from `AGENTS.override.md`.
8. Otherwise return an evidence-based execution report.

# Scope discipline

- You may read and write adjacent files, config, tests, helper scripts, and new files or directories when needed to satisfy the current user step safely.
- Keep the working set minimal and repo-grounded.
- Do not broaden into unrelated cleanup, speculative refactor, or broad rewrite.
- Treat `AGENTS.md`, `README*`, `repo/doc/*`, and similar materials as non-authoritative evidence.
- Do not modify `CLAUDE.md` unless the current user step explicitly targets objective revision.
- Do not commit or push unless explicitly asked.

# Evidence discipline

- Do not claim completion without explicit evidence.
- Report what was read, what was changed, what was run, what remains uncertain, and what remains unverified.
