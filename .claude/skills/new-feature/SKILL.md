---
name: new-feature
description: Pick and build features from SPEC.md by priority. Use when the user says "build the next feature", "/new-feature", "work on X", or "build the <group> group".
---

# New Feature Skill

## Invocation modes

This skill has three modes depending on how it is called:

| Call | Behaviour |
|---|---|
| `/new-feature` | Pick the next P1 item from the backlog and build it |
| `/new-feature <n>` | Build the specific feature described by the user |
| `/new-feature --group "<Name>"` | Build all incomplete items in that feature group, one at a time |

---

## Step 1 — Select the feature

Read `SPEC.md` `### Backlog`.

**Mode: `/new-feature` (no argument)**
Find all `[ ]` items tagged `P1`. Pick the first one in document order.
If no `P1` items remain, list the `P2` items and ask the human to confirm before proceeding.
If the backlog is empty, tell the human and show the prompt template at the bottom of this file.

**Mode: `/new-feature <description>`**
Find the matching item in the backlog. If not found, ask the human to confirm adding it before proceeding.

**Mode: `/new-feature --group "<Name>"`**
Find all `[ ]` items under the named `###` group. Build them one by one in document order, completing and committing each before starting the next. Report progress after each.

---

## Step 2 — Move to In Progress
In `SPEC.md`, move the chosen item from `### Backlog` to `### In Progress`. Commit:
```
docs(spec): move "<feature name>" to in progress
```

---

## Step 3 — Clarify if needed
If the feature description is ambiguous or missing context, ask ONE question before proceeding. Do not ask more than one question at a time.

---

## Step 4 — State a plan
Before writing any code, output a numbered plan (3–8 steps):

```
Plan for: <feature name>

1. <step>
2. <step>
...

Confirm to proceed, or adjust the plan.
```

Wait for the human to confirm or adjust. In `--group` mode, confirm the plan for the first item and proceed without re-confirming for subsequent items unless something unexpected comes up.

---

## Step 5 — Execute step by step
Work through the plan one step at a time. After each step:
- Run lint and type-check on changed files
- Commit with a Conventional Commit (see `.claude/rules/commit-rules.md`)

---

## Step 6 — Run tests
After all steps are done, run the full test suite. Report results. Do not proceed if tests fail.

---

## Step 7 — Definition of Done
Check every item in `.claude/rules/definition-of-done.md`. Confirm all are satisfied.

---

## Step 8 — Close the feature
In `SPEC.md`:
- Move the item from `### In Progress` to `### Done` and mark `[x]`
- Add a changelog entry (see `.claude/rules/doc-sync.md`)

Commit:
```
docs(spec): mark "<feature name>" done [<hash>]
```

In `--group` mode, loop back to Step 1 for the next item in the group.

---

## Prompt Template

When the human asks "how do I add a feature?" output this:

```
## Feature Request

**What:** <one sentence>

**Why:** <user story or business reason>

**Acceptance criteria:**
- [ ] <testable outcome 1>
- [ ] <testable outcome 2>

**Scope:**
- In: <what to build>
- Out: <what NOT to touch>

**Priority:** P1 | P2 | P3

**Notes:** <edge cases, constraints>
```

The human can paste this inline, or add the feature directly to `### Backlog` in `SPEC.md` with a priority tag, then run `/new-feature`.