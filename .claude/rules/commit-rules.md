# Commit Rules
> Follow Conventional Commits on every commit without exception.

## Format
```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

## Types
| Type | Use for |
|---|---|
| `feat` | New user-facing feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | No behaviour change |
| `test` | Adding or fixing tests |
| `chore` | Tooling, deps, config |
| `style` | Formatting only |

## Rules
- Subject line ≤ 72 chars, imperative mood ("add login", not "added login")
- Scope = the area changed, e.g. `auth`, `api/users`, `dashboard`
- Never commit: `.env` files, secrets, build artifacts, `node_modules`
- Never force-push to a protected branch
- One logical change per commit — do not batch unrelated work
- No `TODO`, `FIXME`, or `console.log` in committed code

## Example
```
feat(auth): add magic link login via Resend

- POST /api/auth/magic-link sends 15-min expiry token
- Redirects to /dashboard on valid token

Closes #42
```