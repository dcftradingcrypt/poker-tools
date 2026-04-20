# Decision
Use source-only semantic authority for prompt repair work.

## Context
Prior audits mixed source artifacts, generated continuity outputs, and GPT-only visibility with Codex-readable inputs.

## Decision
For semantic prompt repair and audit:
- source authority is limited to PROMPT_PACK.md, AGENTS.override.md, SKILL.md, and openai.yaml
- PROMPT_PACK.md is GPT-only and not Codex-readable
- generated continuity outputs are not semantic authority for prompt behavior
- end-to-end audit must use one integrated execution line instead of split upstream/downstream passes

## Consequences
This narrows audit input and should reduce criteria drift and repeated rediscovery of the same defect family.

## Open questions
Need to keep validating that every future audit report follows this decision exactly.
