---
name: adopt
description: Onboard an existing codebase into the starter kit. Use when the user says "adopt this project", "add the kit to my existing repo", or "set up the kit on existing code".
---

# Adopt Skill

> ZERO CODE CHANGES during adoption. This skill only reads code and creates/updates
> documentation and kit config files. If you find yourself editing source files,
> tests, or configs that existed before adoption — stop.

---

## Step 1 — Audit the repository

Read the codebase to understand what exists. Run these in order:

```bash
# Structure overview
find . -maxdepth 3 -not -path '*/.git/*' -not -path '*/node_modules/*' \
       -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' \
       | sort

# Existing docs
ls -1 *.md docs/ README* CHANGELOG* 2>/dev/null

# Package / dependency files
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || \
cat go.mod 2>/dev/null || cat Cargo.toml 2>/dev/null

# Git history summary (last 20 commits — reveals what's already been built)
git log --oneline -20 2>/dev/null

# Existing test locations
find . -name '*.test.*' -o -name '*.spec.*' -o -name 'test_*.py' \
   -not -path '*/node_modules/*' | head -20
```

From this audit, infer:
- Tech stack (languages, frameworks, major deps)
- Repo structure (monorepo / single-app / polyrepo service)
- What features appear to already be implemented
- What tests exist and what framework they use
- Whether a CHANGELOG, README, or docs folder already exists

---

## Step 2 — Fill BOOTSTRAP_FORM.md from what you found

Create `.claude/BOOTSTRAP_FORM.md` if it doesn't exist. Pre-fill every field you
can confidently infer from the audit. Mark genuinely unknown fields with `~`.

After writing the file, print a summary:
```
Inferred from codebase:
  Project name:      <name>
  Structure:         <monorepo|single-app|...>
  Frontend:          <yes — Next.js | no>
  Backend:           <yes — FastAPI | no>
  Database:          <PostgreSQL | ~>
  Package manager:   <pnpm>
  ...

Fields marked ~ need your input. Edit .claude/BOOTSTRAP_FORM.md before continuing.
```

Stop and wait for the human to confirm the form is correct before proceeding.

---

## Step 3 — Draft SPEC.md

Create `SPEC.md` at the project root. This is a draft — the human must review it.

**Overview section:** Write one paragraph describing what the project does based
on the README, package description, and git history.

**Tech Stack section:** Fill from the confirmed BOOTSTRAP_FORM.md.

**Features — Done section:** List what already exists as `[x]` items, grouped by
area. Infer from: directory structure, route files, component names, git log,
existing tests. Be conservative — only mark `[x]` if you are confident it exists
and works.

**Features — Backlog section:** If the README, open issues, or TODO comments
reveal planned features, list them as `[ ]` items with a default priority of `P2`.
Leave priority tags for the human to set.

**Out of Scope:** Leave blank — the human fills this.

**Open Questions:** List anything you could not confidently infer:
```
- [ ] Is <X> already implemented or still in progress?
- [ ] What is the intended deployment target?
```

After writing `SPEC.md`, print:
```
Draft SPEC.md written. Before running /new-feature:
  1. Review the Done section — correct any features wrongly marked [x] or missing
  2. Set P1/P2/P3 priority tags on backlog items
  3. Fill in Out of Scope
  4. Resolve Open Questions
```

Stop and wait for human confirmation.

---

## Step 4 — Reconcile existing docs

**If a CHANGELOG already exists:**
- Do not delete or overwrite it
- Add a comment at the top of `docs/CHANGELOG.md`:
  ```
  <!-- History before kit adoption: see <original file> -->
  ```
- Create `docs/CHANGELOG.md` starting from today as `[Unreleased]`
- Leave the original CHANGELOG file in place

**If a README already exists:**
- Do not modify it
- Note in `SPEC.md` Overview: `(see README.md for full detail)`

**If `docs/DECISIONS.md` already exists:**
- Read it and preserve all existing content
- Append a header comment if not already ADR format:
  ```
  <!-- Entries below this line follow ADR format managed by the kit -->
  ```

**If none of these exist:**
- Create `docs/CHANGELOG.md` and `docs/DECISIONS.md` using the standard templates

---

## Step 5 — Create kit files (non-destructive)

Create only files that do not already exist. Never overwrite:

```
.claude/rules/approval-gates.md      ← create if missing
.claude/rules/commit-rules.md        ← create if missing
.claude/rules/definition-of-done.md  ← create if missing
.claude/rules/doc-sync.md            ← create if missing
.claude/skills/*/SKILL.md            ← create all skills if missing
CLAUDE.md                            ← create if missing
```

If any of these already exist, skip them and note which were skipped.

---

## Step 6 — Log adoption as ADR

Add to `docs/DECISIONS.md`:

```markdown
## ADR-001: Adopt agentic coding starter kit
**Date:** <today>
**Status:** Accepted
**Context:** Existing project onboarded into the agentic coding starter kit
**Decision:** Added .claude/ structure, SPEC.md, and docs/ kit files without
modifying existing source code, tests, or configuration
**Consequences:** Future development follows the kit workflow: /new-feature for
feature work, /commit for commits, /milestone at group completion
```

---

## Step 7 — Initial commit

Stage only the new kit files (never stage existing source changes):

```bash
git add CLAUDE.md SPEC.md docs/ .claude/
git status   # verify only kit files are staged
git commit -m "chore: adopt agentic coding starter kit"
```

If `git status` shows unexpected files staged, unstage them and stop.

---

## Step 8 — Print handoff summary

```
Adoption complete.

Files created:
  CLAUDE.md
  SPEC.md              ← REVIEW THIS before running /new-feature
  docs/CHANGELOG.md
  docs/DECISIONS.md
  .claude/             ← full kit structure

Files left unchanged:
  <list any pre-existing docs that were preserved>

Next steps:
  1. Review SPEC.md — correct Done items, set priorities, fill Out of Scope
  2. Answer the Open Questions in SPEC.md
  3. Run /new-feature when ready to build
```