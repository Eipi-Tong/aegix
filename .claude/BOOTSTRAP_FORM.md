# BOOTSTRAP FORM
> Fill in this file before running `/project:bootstrap`.
> The agent will read your answers and scaffold the project accordingly.
> Leave any field as `~` if you want the agent to recommend a default.

---

## 1. Project Identity

```
Project name:       ~
Short description:  ~
Primary language:   ~        # e.g. TypeScript, Python, Go
Target platform:    ~        # e.g. web, mobile-web, desktop, API-only
```

---

## 2. Repository Structure

```
Structure:          ~        # monorepo | polyrepo | single-app
# monorepo   → frontend/ backend/ packages/ all in one repo
# polyrepo   → separate repos per service (agent will only scaffold one at a time)
# single-app → no backend, frontend only (or backend only)

Top-level dirs:     ~        # only for monorepo — e.g. apps/web, apps/api, packages/ui
```

---

## 3. Frontend

```
Include frontend:   ~        # yes | no

Framework:          ~        # Next.js | Remix | SvelteKit | Nuxt | Vite+React | Vue | none
Styling:            ~        # Tailwind | CSS Modules | styled-components | UnoCSS | none
Component lib:      ~        # shadcn/ui | Radix | MUI | Chakra | none
State management:   ~        # Zustand | Jotai | Redux Toolkit | React Query | none
Auth (frontend):    ~        # NextAuth | Clerk | Supabase Auth | none
```

---

## 4. Backend

```
Include backend:    ~        # yes | no

Runtime:            ~        # Node.js | Python | Go | Rust | none
Framework:          ~        # Express | Fastify | Hono | FastAPI | Django | Gin | none
Database:           ~        # PostgreSQL | MySQL | SQLite | MongoDB | none
ORM / query:        ~        # Prisma | Drizzle | SQLAlchemy | GORM | raw SQL | none
Auth (backend):     ~        # JWT | session | Supabase | Auth.js | none
API style:          ~        # REST | tRPC | GraphQL | none
```

---

## 5. Infrastructure & Deployment

```
Containerize:       ~        # yes | no  (generates Dockerfile + docker-compose)
Cloud target:       ~        # Vercel | Railway | Fly.io | AWS | GCP | self-hosted | none
CI/CD:              ~        # GitHub Actions | GitLab CI | none
Environment vars:   ~        # .env.local | Doppler | AWS Secrets | none
```

---

## 6. Tooling

```
Package manager:    ~        # npm | pnpm | yarn | bun | pip | uv
Linter:             ~        # ESLint | Biome | Ruff | none
Formatter:          ~        # Prettier | Biome | Black | none
Testing framework:  ~        # Vitest | Jest | Pytest | Playwright | none
Git hooks:          ~        # Husky + lint-staged | lefthook | none
Commit convention:  ~        # Conventional Commits | none
```

---

## 7. Agent Behaviour Preferences

```
Auto-commit:        ~        # yes | no  (agent commits after every completed task)
Doc sync:           ~        # yes | no  (agent updates SPEC.md when code changes)
PR descriptions:    ~        # yes | no  (agent writes PR body on push)
Notify on:          ~        # commit | pr | never  (when agent should pause for human review)
```

---

## 8. Team & Context

```
Solo or team:       ~        # solo | team
Main branch:        ~        # main | master
Protected branches: ~        # e.g. main, staging
Code review:        ~        # required | optional | none
```

---

## 9. Anything Else

```
Notes for agent:    ~
# Add anything that doesn't fit above — special constraints, existing services to integrate,
# non-standard folder conventions, etc.
```