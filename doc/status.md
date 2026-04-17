## 2026-03-30 00:00 three-actor-contract-reset
- Request: Adopt the AGENTS.md-style process instead of continuing ad hoc repair and audit.
- Plan: Create persistent docs, restate scope and assumptions, then continue source-only end-to-end repair under a documented method.
- Actions: Created repo/doc/ structure; added README.md, architecture.md, overview spec, and initial worklog memo.
- Files changed: repo/doc/README.md; repo/doc/architecture.md; repo/doc/specs/overview.md; repo/doc/worklog/2026-03-30-three-actor-contract-reset.md; repo/doc/status.md.
- Verification: Verified files were created and contents align with current task scope.
- Docs updated: README.md; architecture.md; specs/overview.md; worklog memo; status.md.
- Open issues: Need subsystem specs and then a fresh end-to-end semantic audit under the documented method.
- Next step: Split subsystem specs and run the next audit against the source contract artifacts only.

## 2026-03-30 00:20 three-actor-contract-spec-split
- Request: Split the working method into stable subsystem specs so future audits check the same boundaries each time.
- Plan: Create specs for actor/visibility, routing/stop, normal repo work, and continuity refresh; add a decision log that fixes source-only authority.
- Actions: Added 4 subsystem specs and 1 decision-log entry.
- Files changed: repo/doc/specs/actor-authority-and-visibility.md; repo/doc/specs/routing-and-stop.md; repo/doc/specs/normal-repo-work.md; repo/doc/specs/continuity-refresh.md; repo/doc/decision-log/2026-03-30-source-authority-and-visibility.md; repo/doc/status.md.
- Verification: Verified all new docs exist and reflect the current known contract boundaries and open issues.
- Docs updated: specs/actor-authority-and-visibility.md; specs/routing-and-stop.md; specs/normal-repo-work.md; specs/continuity-refresh.md; decision-log/2026-03-30-source-authority-and-visibility.md; status.md.
- Open issues: Need a scenario matrix and then a fresh source-only end-to-end audit against the current source files.
- Next step: Build the scenario matrix and classify real defects by execution impact only.

## 2026-03-30 00:40 three-actor-contract-scenario-matrix
- Request: Prevent missed scenarios by enumerating the end-to-end cases that every audit must cover.
- Plan: Build one minimum scenario matrix covering control/routing, repo work, continuity refresh, visibility/authority, and stop behavior.
- Actions: Added scenario matrix under repo/doc/research with 26 end-to-end scenarios.
- Files changed: repo/doc/research/2026-03-30-scenario-matrix.md; repo/doc/status.md.
- Verification: Verified the matrix exists and covers the defect families already seen in prior work.
- Docs updated: research/2026-03-30-scenario-matrix.md; status.md.
- Open issues: Need to run the current source artifacts against this exact matrix and classify only execution-changing defects.
- Next step: Perform the source-only matrix audit against the current prompt-contract artifacts.
