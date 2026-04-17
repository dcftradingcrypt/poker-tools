# Three-Actor Runtime Contract Architecture

Actors:
- User: decisions, input supply, relay, git actions
- GPT: startup interpretation, routing, audit, review, text authoring, user-facing orchestration
- Codex: repo-local read/edit/execute/verify inside active CODEX_TASK scope

Primary artifacts under repair:
- PROMPT_PACK.md: GPT-only external contract
- AGENTS.override.md: Codex execution contract
- .agents/skills/handoff-packet/SKILL.md: continuity refresh contract
- .agents/skills/handoff-packet/agents/openai.yaml: metadata only

Core correctness dimensions:
- actor authority boundaries
- GPT-visible vs Codex-readable visibility boundaries
- route -> execute -> write alignment
- user-owned stop vs lane-local failure separation
- continuity refresh source selection and output behavior
