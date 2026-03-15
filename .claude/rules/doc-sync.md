# Doc Sync Rules
> Apply these rules after every completed task when `doc sync: yes` in BOOTSTRAP_FORM.md.

## SPEC.md Updates
1. Find the feature section matching what you just built
2. Change `[ ]` to `[x]` for completed items
3. Add one line to `## Changelog`:
   ```
   | YYYY-MM-DD | abc1234 | <what changed> |
   ```
4. Commit as a separate docs commit:
   ```
   docs(spec): mark <feature> complete [abc1234]
   ```

## DECISIONS.md Updates
Add an entry when:
- A new library or tool is introduced
- An architectural pattern is chosen
- A previous decision is reversed

Entry format:
```markdown
## ADR-<N>: <Short title>
**Date:** YYYY-MM-DD
**Status:** Accepted
**Context:** Why this decision was needed
**Decision:** What was chosen
**Consequences:** What this affects going forward
```

## What NOT to Change
- Do not rewrite sections the human wrote
- Do not change feature descriptions, only status markers
- Do not delete changelog entries