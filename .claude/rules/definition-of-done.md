# Definition of Done
> A task is complete only when ALL of the following are true.
> Check this list before every commit.

- [ ] Code works as described in the feature request
- [ ] No lint or type errors in changed files (`pnpm lint`, `tsc --noEmit`, or equivalent)
- [ ] Tests exist for new logic (unit) and new routes/pages (integration), if a test framework is configured
- [ ] No `TODO`, `FIXME`, or `console.log` in committed code — use `// NOTE:` for intentional callouts
- [ ] `SPEC.md` updated to reflect the completed feature (status markers and changelog)
- [ ] Commit message follows Conventional Commits (see `commit-rules.md`)

## On Failing Tests
Do not paper over failing tests. If tests fail after your changes:
1. Report the failure immediately
2. Fix the root cause before committing
3. If the test itself is wrong, explain why and ask the human before deleting it