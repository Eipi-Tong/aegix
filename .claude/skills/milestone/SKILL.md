---
name: milestone
description: Close a feature group as a milestone. Writes docs, proposes E2E tests, and runs a go/no-go gate. Use when the user says "/milestone", "this group is done", or the agent detects all items in a group are complete.
---

# Milestone Skill

> A milestone is a deliberate human decision, not an automatic event.
> The agent proposes; the human approves at every gate.
> Never advance past a gate without explicit confirmation.

---

## Invocation

```
/milestone "<name> — <one sentence framing>"
```

Example:
```
/milestone "Core Simulator complete — cache, engine, and scheduler can now run end-to-end"
```

If called without a name or framing sentence, ask for both before proceeding.

---

## Step 1 — Verify completion

Read `SPEC.md`. Find the feature group named in the milestone call.

Check every item in that group:
- All items must be `[x]` (Done) before proceeding
- If any `[ ]` items remain, list them and stop:
  ```
  Cannot close milestone — these items are still open:
    - [ ] <feature>
    - [ ] <feature>

  Complete them first, or explicitly move them to a future milestone.
  ```

If items need to be deferred, ask the human:
```
Move these to a new group "<name> — v2"? (yes / no / list which ones)
```
Wait for confirmation before touching SPEC.md.

---

## Step 2 — Write CHANGELOG.md entry

Open `docs/CHANGELOG.md`. Promote the `[Unreleased]` section to a named version.

Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [<milestone-name>] — <YYYY-MM-DD>

### Added
- <user-facing description of what's now possible — not internal task names>
- <one line per significant capability>

### Changed
- <anything that changed existing behaviour>

### Fixed
- <bugs fixed during this milestone, if any>
```

Rules:
- Write for a developer reading the project, not for the agent's internal log
- Do not copy feature names verbatim from SPEC.md — rewrite as user-facing capabilities
- Keep each line to one sentence
- After writing, add a fresh `## [Unreleased]` section above it for the next milestone

---

## Step 3 — Write / update ARCHITECTURE.md

Open or create `docs/ARCHITECTURE.md`.

For the completed milestone group, write or update a section describing:
- What this layer/subsystem does
- How it is structured (key files, entry points)
- How it connects to other parts of the system
- Any non-obvious design decisions (cross-reference relevant ADRs by number)

Format:
```markdown
## <Group Name>
_Added in milestone: <milestone-name>, <date>_

### Purpose
<one paragraph — what problem this solves>

### Structure
| File / Module | Responsibility |
|---|---|
| `<path>` | <what it does> |

### Key design decisions
- See ADR-<N>: <title>

### Interfaces
<How other parts of the system interact with this layer>
```

Do not rewrite sections for groups not covered by this milestone.

---

## Step 4 — Add milestone marker to SPEC.md

In `SPEC.md` `## Changelog`, add a milestone divider above the most recent feature entries:

```markdown
| <date> | — | **Milestone: <name>** |
```

This groups the changelog visually so it's clear which features shipped together.

---

## Step 5 — Commit documentation

```bash
git add docs/CHANGELOG.md docs/ARCHITECTURE.md SPEC.md
git commit -m "docs(milestone): <milestone-name>"
```

---

## Step 6 — Propose E2E test scenarios

Based on the completed features, propose user journey scenarios for E2E tests.
Write them as plain descriptions — not code yet.

Format:
```
Proposed E2E scenarios for milestone: <name>

1. <Scenario name>
   As a <user>, I <action>, and expect <outcome>.
   Covers: <list of features this tests>

2. <Scenario name>
   ...
```

Rules for good scenarios:
- Each scenario tests a complete user journey, not a unit of code
- Scenarios should cross feature boundaries where possible (that's the point of E2E)
- Aim for 3–6 scenarios per milestone — enough to cover the happy paths and one or two key failure modes
- Do not propose a scenario for every feature individually

Then ask:
```
Review these E2E scenarios:
  - Approve all → I'll write the tests
  - Edit the list → tell me what to add, remove, or change
  - Skip E2E for this milestone → say "skip"
```

**Wait for human decision before writing any test code.**

---

## Step 7 — Write E2E tests (if approved)

Once the human approves or edits the scenario list:

1. Check `BOOTSTRAP_FORM.md` for the configured test framework
2. Write E2E tests in the appropriate location:
   - Playwright → `e2e/<milestone-slug>/`
   - Pytest → `tests/e2e/<milestone-slug>/`
   - Other → ask the human where they want them
3. Run the tests:
   ```bash
   # example for Playwright
   npx playwright test e2e/<milestone-slug>/
   ```
4. Report results. If tests fail:
   - Fix the test code if the failure is a test authoring error
   - Report to the human if the failure reveals a real bug — do not mask it
5. Commit:
   ```bash
   git add e2e/  # or tests/e2e/
   git commit -m "test(e2e): add E2E scenarios for <milestone-name>"
   ```

---

## Step 8 — Go / No-Go gate

Present the milestone summary to the human:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Milestone: <name>
Date: <today>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Features completed:  <N>
E2E tests:           <passing N / skipped>
Docs written:        CHANGELOG.md, ARCHITECTURE.md, SPEC.md marker

Checklist:
  [x] All features in group marked Done
  [x] CHANGELOG.md updated
  [x] ARCHITECTURE.md updated
  [x] E2E tests written and passing  (or: skipped by human)
  [ ] Human go/no-go decision

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GO   → tag this milestone and move to the next group
NO-GO → list what needs fixing first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Wait for explicit GO or NO-GO. Do not proceed without it.**

---

## Step 9 — On GO: tag the release

```bash
# Determine next version tag from git tags
git tag --sort=-v:refname | head -5

# Tag the milestone
git tag -a v<X.Y.0> -m "Milestone: <name>"
git push origin v<X.Y.0>   # only if remote is configured
```

Version convention:
- First milestone → `v0.1.0`
- Each subsequent milestone group → bump minor (`v0.2.0`, `v0.3.0`)
- Bug-fix-only milestone → bump patch (`v0.1.1`)

If the human wants a different version number, ask before tagging.

Print final summary:
```
Milestone closed.
  Tag:      v<X.Y.0>
  Docs:     docs/CHANGELOG.md, docs/ARCHITECTURE.md
  Next:     run /new-feature to begin the next group
```

---

## Step 10 — On NO-GO: create a fix list

Ask the human what must be resolved:
```
What needs to be fixed before this milestone can be marked GO?
(List issues — I'll track them in SPEC.md Open Questions)
```

Add each item to `## Open Questions` in `SPEC.md`:
```
- [ ] [BLOCKING v<X.Y.0>] <issue description>
```

Commit:
```bash
git commit -m "docs(spec): add blocking issues for milestone <name>"
```

The milestone remains open. Run `/milestone "<name> — <framing>"` again
once the blocking issues are resolved.