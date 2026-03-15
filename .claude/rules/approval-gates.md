# Approval Gates
> Stop and ask the human before doing any of the following.
> Do not proceed until you receive explicit confirmation.

| Action | Reason |
|---|---|
| Adding a dependency not in `BOOTSTRAP_FORM.md` | May conflict with stack choices |
| Destructive database schema change (drop, rename column) | Data loss risk |
| Modifying `Dockerfile`, `docker-compose.yml`, or `.github/` | Infrastructure side effects |
| Pushing to a protected branch | Human owns releases |
| Deleting more than one file at a time | Easy to misinterpret scope |
| Calling an external service API with real data | Irreversible side effects |
| Renaming environment variables | Breaks deployments silently |
| Any action that contradicts `docs/DECISIONS.md` | Consistency |

## How to Ask
State clearly:
1. What you were about to do
2. Why you think it's needed
3. What the alternatives are

Then stop and wait.