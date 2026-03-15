---
name: sync-docs
description: Update SPEC.md and docs/DECISIONS.md to reflect recent code changes. Use after completing a feature, or when the user says "sync docs", "update the spec", or "log this decision".
---

# Sync Docs Skill

## When called after a feature
1. Read the most recent git log (`git log --oneline -10`) to identify what changed
2. Open `SPEC.md` and mark completed items `[x]`
3. Add a changelog entry:
   ```
   | YYYY-MM-DD | <short hash> | <what changed> |
   ```
4. Commit:
   ```
   docs(spec): mark <feature> complete [<hash>]
   ```

## When called after an architectural decision
Ask the human:
- What was decided?
- Why?
- What does it affect?

Then add an ADR entry to `docs/DECISIONS.md`:
```markdown
## ADR-<N>: <Short title>
**Date:** YYYY-MM-DD
**Status:** Accepted
**Context:** <why>
**Decision:** <what>
**Consequences:** <impact>
```

Commit:
```
docs(decisions): add ADR-<N> <short title>
```

## Guardrails
- Never rewrite sections the human authored
- Never delete changelog entries
- Never change feature descriptions, only their status markers