---
name: commit
description: Create a well-formed Conventional Commit. Use when the user says "commit", "commit my changes", or asks you to save progress.
disable-model-invocation: true
---

# Commit Skill

## Step 1 — Check the working tree
```bash
git status
git diff --stat
```
If the tree is clean, tell the user and stop.

## Step 2 — Check for violations
Before committing, verify:
- No `.env` or secret files staged
- No `console.log`, `TODO`, or `FIXME` in staged files
- No build artifacts or `node_modules` staged

If violations found, list them and stop. Do not commit.

## Step 3 — Run quality checks
Run the project's lint and type-check commands (from `BOOTSTRAP_FORM.md` tooling section).
If they fail, stop and report.

## Step 4 — Compose the message
Choose the correct type from `.claude/rules/commit-rules.md`.
Draft the commit message and show it to the user for confirmation before committing.

Format:
```
<type>(<scope>): <description>

[body if needed]
```

## Step 5 — Commit
```bash
git add -p   # stage interactively if multiple logical changes
git commit -m "<message>"
```

## Step 6 — Confirm
Print the commit hash and subject line. Ask if the user wants to push.