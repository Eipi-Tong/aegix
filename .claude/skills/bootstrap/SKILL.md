---
name: bootstrap
description: Scaffold a new project from BOOTSTRAP_FORM.md. Use when the user says "bootstrap the project", "set up the project", or runs /bootstrap for the first time.
---

# Bootstrap Skill

## Step 1 — Validate the form
Read `.claude/BOOTSTRAP_FORM.md`. Check that these fields are filled (not `~`):
- Project name
- Structure (monorepo / polyrepo / single-app)
- Frontend: yes/no (and framework if yes)
- Backend: yes/no (and runtime if yes)

If any required field is missing, list them and stop. Do not guess or use defaults without asking.

## Step 2 — Generate directory structure
Based on the filled form:

**monorepo:**
```
apps/
  web/       ← if frontend: yes
  api/       ← if backend: yes
packages/    ← if monorepo has shared code
```

**single-app (frontend only):**
```
src/
public/
```

**single-app (backend only):**
```
src/
tests/
```

## Step 3 — Generate config files
Create starter config files matching the chosen stack. Examples:
- `package.json` / `pyproject.toml` with correct deps
- `tsconfig.json` if TypeScript
- `.eslintrc` / `biome.json` if linter chosen
- `.env.example` with placeholder keys
- `Dockerfile` + `docker-compose.yml` if containerize: yes
- `.github/workflows/ci.yml` if CI/CD: GitHub Actions

## Step 4 — Generate SPEC.md

Based on the project description and stack in `BOOTSTRAP_FORM.md`, infer a realistic feature list grouped by area (e.g. Core, API, Dashboard, Auth). For each feature:
- Write a short, specific description (one line)
- Assign a default priority: `P1` for foundational features, `P2` for important but non-blocking, `P3` for enhancements
- Group features under `###` headings by area

Tell the human after generating:
> "These features were inferred from your project description. Edit priorities (`P1`/`P2`/`P3`) and add or remove items before running `/new-feature`."

Use this structure:

```markdown
# SPEC.md

_Last updated: <date>_

## Overview
<Short description from BOOTSTRAP_FORM.md>

## Tech Stack
| Layer | Choice |
|---|---|
<rows from BOOTSTRAP_FORM.md>

## Features

<!--
HUMAN: Mark priorities with P1 / P2 / P3 tags. Agent picks the next P1 when you run /new-feature.
AGENT: Never reword descriptions or change priority tags. Only update [ ]/[x] and move items between sections.
-->

### In Progress
_Nothing in progress yet._

### Backlog

#### <Group 1>
- [ ] <feature> `P1`
- [ ] <feature> `P2`

#### <Group 2>
- [ ] <feature> `P1`
- [ ] <feature> `P3`

### Done
_Nothing done yet._

## Out of Scope
- —

## Open Questions
- —

## Changelog
| Date | Commit | Change |
|------|--------|--------|
| <date> | — | Initial scaffold |
```

## Step 5 — Generate docs/DECISIONS.md
Log the initial tech choices using ADR format (see `.claude/rules/doc-sync.md`).
Start with ADR-001 for the repo structure choice, ADR-002 for frontend stack, ADR-003 for backend stack.

## Step 6 — Init git and commit
```bash
git init
git add .
git commit -m "chore: initial project scaffold"
```

## Step 7 — Print summary
List what was created and tell the human what to do next:
1. Review and adjust priorities in `SPEC.md` (`P1` = build first)
2. Run `/new-feature` to start building — agent picks the next `P1` item
3. Run `/new-feature --group "<name>"` to build a whole feature group at once