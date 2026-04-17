# Task
Adopt the AGENTS.md-style work cycle for the three-actor runtime contract repair and stop ad hoc, criteria-shifting audits.

# Context
Affected artifacts:
- PROMPT_PACK.md
- AGENTS.override.md
- SKILL.md
- openai.yaml

Prior failure pattern:
- source / generated / GPT-only / Codex-readable boundaries were not enforced consistently during audit
- local fixes were made without complete propagation checks
- route and execution were sometimes audited separately instead of end-to-end

# Assumptions
- PROMPT_PACK.md is GPT-only external contract attached to the GPT project
- Codex does not directly read PROMPT_PACK.md
- generated continuity artifacts are not semantic authority for prompt behavior
- the user wants a repair workflow that is narrow, documented, and verification-driven

# Options considered
1. Continue with conversational-only auditing.
2. Create a minimal persistent doc structure and use it as the working control plane.

# Chosen approach
Use option 2.
Create persistent docs under repo/doc/ to hold:
- stable overview spec
- architecture summary
- status log
- worklog for reasoning and verification plan

# Impact
This does not yet change the source contract semantics. It changes the working method and makes subsequent audits traceable.

# Verification
- created repo/doc/ hierarchy
- created README.md, architecture.md, specs/overview.md
- created initial worklog memo and status entry

# Open questions
- whether additional subsystem specs should be split out immediately (actor boundaries, routing, continuity, write authority)
- which open defects from the current conversational audit should be treated as root defects first
