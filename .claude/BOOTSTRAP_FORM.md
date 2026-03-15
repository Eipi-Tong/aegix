# BOOTSTRAP FORM
> Adopted from existing codebase on 2026-03-15.
> Fields inferred from audit; mark `~` fields still need your input.

---

## 1. Project Identity

```
Project name:       aegix
Short description:  A secure, observable sandbox runtime for AI agent tool execution
Primary language:   Python
Target platform:    API-only / library + CLI
```

---

## 2. Repository Structure

```
Structure:          single-app   # Python monolith with 3 packages: aegix_core, aegix_cli, aegix_agent

Top-level dirs:     aegix_core/ aegix_cli/ aegix_agent/ examples/
```

---

## 3. Frontend

```
Include frontend:   no
```

---

## 4. Backend

```
Include backend:    yes

Runtime:            Python 3.11
Framework:          none (library + Typer CLI)
Database:           none
ORM / query:        none
Auth (backend):     none
API style:          none (library / CLI; future: REST gateway planned)
```

---

## 5. Infrastructure & Deployment

```
Containerize:       yes   # uses Docker SDK to spin up ephemeral containers
Cloud target:       ~     # not yet determined
CI/CD:              none
Environment vars:   .env  # aegix_agent/.env (OpenAI key)
```

---

## 6. Tooling

```
Package manager:    pip   # pyproject.toml + hatchling build backend
Linter:             ruff     # none configured yet
Formatter:          ~     # none configured yet
Testing framework:  pytest     # none configured yet (no tests exist)
Git hooks:          none
Commit convention:  Conventional Commits
```

---

## 7. Agent Behaviour Preferences

```
Auto-commit:        yes
Doc sync:           yes
PR descriptions:    yes
Notify on:          pr
```

---

## 8. Team & Context

```
Solo or team:       solo
Main branch:        main
Protected branches: main
Code review:        optional
```

---

## 9. Anything Else

```
Notes for agent:
- aegix_core is the main library; aegix_cli is the Typer CLI entry point; aegix_agent contains example agent runners
- Docker is used as the sandbox backend — docker daemon must be running
- Resource limits (cpu, mem_mb, pids, timeout_s) are defined in models but NOT yet enforced in docker_backend.py
- Network mode and FS rules are also not yet enforced in docker_backend.py
- aegix_core/cli.py and aegix_core/router.py have import path inconsistencies (use `aegix.*` but package is `aegix_core`)
- aegix_cli/main.py is currently empty (1 line)
```
