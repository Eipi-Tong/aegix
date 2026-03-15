# CLAUDE.md
> Agent operating manual. Read this first, every session.

## Session Start
1. Read `.claude/BOOTSTRAP_FORM.md` — stack, structure, preferences
2. Read `SPEC.md` if it exists — current feature state
3. Run `git status` — never assume a clean tree
4. State your understanding of the task before writing code

## Role
You write code, maintain docs, and manage git for this project.
You do not make product decisions or choose tech stacks.

## Core Rules
- Follow the stack defined in `.claude/BOOTSTRAP_FORM.md`. Do not add new dependencies without asking.
- Follow Conventional Commits for every commit. See `.claude/rules/commit-rules.md`.
- A task is not done until it passes the Definition of Done. See `.claude/rules/definition-of-done.md`.
- Some actions require human approval before you proceed. See `.claude/rules/approval-gates.md`.
- Keep docs in sync after every completed task. See `.claude/rules/doc-sync.md`.

## Skills Available
- `/bootstrap` — scaffold a new project from `.claude/BOOTSTRAP_FORM.md`
- `/adopt` — onboard an existing repo into the kit (audit → draft SPEC.md → kit files)
- `/new-feature` — pick and build the next feature from `SPEC.md`
- `/milestone "<n> — <framing>"` — close a feature group: docs, E2E tests, go/no-go gate
- `/refactor` — plan and execute a refactor with preserved behaviour
- `/sync-docs` — update `SPEC.md` and `docs/DECISIONS.md` after out-of-band changes
- `/commit` — guided commit with Conventional Commits enforcement
