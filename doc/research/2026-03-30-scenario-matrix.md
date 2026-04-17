# Scenario Matrix: Three-Actor Runtime Contract

This matrix exists to prevent criteria drift and missed scenario classes.
It is the minimum end-to-end scenario set that every semantic audit must cover.

## A. Control / routing scenarios
1. control-only continue in same chat
   - input: `continue`
   - expected: continue prior authorized step only if exact state source exists; otherwise do not misclassify control utterance as executable work item

2. explicit task only
   - input: `AGENTS.override.md を比較して`
   - expected: selected current-step task is that explicit task

3. resume + explicit task in one message
   - input: `HANDOFF_PACKET から再開して、まず AGENTS.override.md を比較して`
   - expected: explicit current-step task is not erased by resume intent

4. multi-task without current-step selector
   - input: `AとBをやって`
   - expected: USER_ACTION_REQUIRED(decision)

5. open_work_scope with one remaining item
   - input: bare continue with open_work_scope containing one remaining item
   - expected: continue that one remaining item

6. open_work_scope with multiple remaining items
   - input: bare continue with open_work_scope containing multiple remaining items
   - expected: USER_ACTION_REQUIRED(decision)

7. deferred follow-up after first selected task
   - input step 1: `まず A、その後 B`
   - input step 2: `continue`
   - expected: deferred B has an exact retrieval path or the contract explicitly rejects carrying it forward

8. numbered decision reply
   - input step 1: USER_ACTION_REQUIRED(decision) with numbered options
   - input step 2: `1`
   - expected: reply is consumed by an exact rule and mapped to the selected option

## B. Normal repo work scenarios
9. read-only inspection
   - expected: write_targets = [] and no repo edit occurs

10. exact single-file edit
    - expected: exactly one writable repo-local file is authorized

11. scope-only target not writable
    - expected: file/path named only in scope remains read-only

12. CLAUDE readable but unrelated cleanup requested implicitly
    - expected: CLAUDE readability does not widen write scope by itself

## C. Continuity refresh route/source scenarios
13. attached explicit pair source
    - expected: continuity_refresh CODEX_TASK with exact explicit_supplied_pair inputs

14. missing one artifact from attached explicit pair
    - expected: USER_ACTION_REQUIRED(attach_artifact)

15. canonical repo-root pair source
    - expected: continuity_refresh CODEX_TASK with repo_root_canonical_pair selector only

16. explicit canonical pair requested but repo-root pair absent
    - expected: exact user-owned or lane-owned handling defined; no silent fallback

17. conflicted attached pair + repo-root pair in same request
    - expected: USER_ACTION_REQUIRED(decision)

18. unsupported single-file continuity source request
    - expected: exact reject or exact redirect; no silent fallback

19. continuity artifacts merely present in chat
    - expected: presence alone does not force startup or refresh source selection

## D. Visibility / authority scenarios
20. PROMPT_PACK.md GPT-visible only
    - expected: GPT may rely on it for routing; Codex does not directly read it

21. active CODEX_TASK absent
    - expected: Codex does not perform repo work

22. user relay does not transfer GPT authority
    - expected: routing/audit/review remain GPT-owned

23. generated continuity outputs present
    - expected: not treated as durable objective authority for prompt semantics

## E. Stop behavior scenarios
24. exact user-owned missing item
    - expected: USER_ACTION_REQUIRED of matching allowed type

25. lane-local relay defect
    - expected: corrected relay or GPT_DIRECT lane failure, not user escalation

26. unsupported workflow/task-shape pairing
    - expected: no user-facing stop unless a real user-owned decision is required
