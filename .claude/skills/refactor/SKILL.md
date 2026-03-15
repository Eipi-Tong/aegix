---
name: refactor
description: Plan and execute a code refactor with preserved behaviour. Use when the user asks to refactor, clean up, simplify, extract, or reorganise existing code without changing what the app does.
---

# Refactor Skill

## Step 1 — Parse the request
Identify:
- **Target:** Which file(s), module(s), or area of the codebase
- **Goal:** What kind of refactor (extract function/component, rename for clarity, split file, remove duplication, simplify logic, reorganise imports, etc.)
- **Constraint:** Behaviour must stay the same (no new features, no breaking API changes)

If any of these are unclear, ask ONE clarifying question. Do not guess scope.

## Step 2 — State a plan
Before changing code, output a short plan. Include:

```
Plan for: <refactor name>

1. <first change — e.g. Extract X into Y>
2. <second change>
…
N. Run tests to confirm behaviour unchanged

- In scope: <what will change>
- Out of scope: <what will NOT change>
- Behaviour: preserved (existing tests must still pass)

Confirm to proceed, or adjust the plan.
```

Wait for the human to say "go" or modify the plan.

## Step 3 — Execute step by step
- Make small, logical changes. One commit per logical step where possible.
- After each step: run lint and type-check on changed files.
- Commit with Conventional Commits (see `.claude/rules/commit-rules.md`). Use type `refactor:` for refactor-only commits, e.g. `refactor(api): extract validation into helper`.

## Step 4 — Verify behaviour
- Run the full test suite. If no tests exist for the touched area, run the app manually or describe how the human can verify.
- Do not proceed if tests fail; fix the cause (refactor or test) before committing.

## Step 5 — Check Definition of Done
Go through `.claude/rules/definition-of-done.md`. Ensure no new lint/type errors, no stray TODOs or console.logs, and commits follow the convention.

## Step 6 — Sync docs (if needed)
If the refactor changes architecture or public APIs, run the doc sync procedure from `.claude/rules/doc-sync.md` (e.g. update DECISIONS.md with an ADR). For internal-only refactors, skip.

---

## Prompt Template (give this to the human on request)

When the user asks "how do I request a refactor?" or "give me the refactor template", output:

```
## Refactor Request

**Target:** <file(s), module(s), or area — e.g. "src/api/auth.ts", "checkout flow">

**Goal:** <what to improve — e.g. extract repeated logic, rename for clarity, split large file>

**Constraint:** Behaviour unchanged. Existing tests (or manual checks) must still pass.

**Out of scope:** <what NOT to change — e.g. API contract, UI copy>
```
