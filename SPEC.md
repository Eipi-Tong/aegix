# Aegix — Project Spec

> (see README.md for full detail)

## Overview

Aegix is a secure, observable sandbox runtime designed to execute AI agent tool calls — shell commands, Python scripts, and filesystem operations — in ephemeral, isolated Docker containers. It sits between an AI agent (or human operator) and the host system, enforcing policy guardrails, applying resource limits, producing structured audit logs, and persisting execution artifacts. The project is currently at MVP stage and is structured as three Python packages: `aegix_core` (runtime library), `aegix_cli` (Typer CLI), and `aegix_agent` (example agent runners).

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11 |
| CLI framework | Typer |
| Sandbox backend | Docker SDK (`docker` Python package) |
| Policy config | YAML |
| Data models | `dataclasses` |
| Example agent | OpenAI SDK (`gpt-4o` tool calls) |
| Linter | ruff |
| Test framework | pytest |
| Package manager | pip (pyproject.toml + hatchling) |
| Commit convention | Conventional Commits |

---

## Features

### Done

#### Core Runtime (`aegix_core`)
- [x] Fix import paths — all `aegix_core` modules use correct `aegix_core.*` imports; CLI entry point wired to `aegix_core.cli:app`
- [x] Remove `aegix_cli` stub package — `aegix_core/cli.py` is the sole CLI entry point
- [x] Enforce resource limits — `nano_cpus`, `mem_limit`, `pids_limit` applied on container create; `timeout` command enforces wall-clock timeout on exec
- [x] Enforce network mode — `none`/`bridge`/`host` mapped to Docker; `allowlist` uses bridge
- [x] Enforce FS rules — container root is read-only; `write_paths` get tmpfs mounts; `read_only_paths` are bind-mounted `:ro` from host
- [x] Unit tests for `PolicyEngine` — 18 tests covering deny patterns, allow-list mode, network allowlist guard, per-tool limits; fixed `r.research` → `r.search` bug
- [x] Unit tests for `ToolRouter` — 20 tests covering validation, policy deny, exec success/failure, container cleanup
- [x] Integration tests for `DockerBackend` — 17 tests covering create/destroy, exec, resource limits, network modes, FS rules
- [x] `ToolCall` / `ToolContext` data models (`aegix_core/models.py`)
- [x] `AegixError` typed error model with error type literals (`aegix_core/errors.py`)
- [x] `PolicyConfig` + `load_policy()` from YAML (`aegix_core/policy.py`)
- [x] `PolicyEngine.evaluate()` — deny pattern matching, allow-list mode, network allowlist guard (`aegix_core/policy.py`)
- [x] Default policy YAML with sensible deny patterns (`aegix_core/policy/default.yaml`)
- [x] `DockerBackend` — create / exec / destroy ephemeral containers (`aegix_core/runtime/docker_backend.py`)
- [x] `AuditLogger` — append-only JSONL event log (`aegix_core/logging/audit.py`)
- [x] `ArtifactWriter` — persist `stdout.txt`, `stderr.txt`, `exit_code.txt`, `report.json` (`aegix_core/io/artifacts.py`)
- [x] `ToolRouter.handle()` — full pipeline: validate → policy → exec → artifacts → audit (`aegix_core/router.py`)
- [x] `ToolInvocation` contract dataclass (`aegix_core/contracts.py`)

#### CLI (`aegix_cli`)
- [x] CLI skeleton with Typer app (`aegix_core/cli.py`)

#### Example Agent (`aegix_agent`)
- [x] OpenAI runner example — LLM tool call → Aegix exec loop (`aegix_agent/openai_runner.py`)

---

### Backlog

#### Observability (P2)
- [ ] **[P2]** `dump_effective_policy()` — expose as CLI subcommand (`aegix policy dump`)
- [ ] **[P2]** Structured run summary printed to stdout after each execution
- [ ] **[P2]** Run directory naming with timestamp + run_id for easy correlation

#### REST Gateway (P3)
- [ ] **[P3]** HTTP API server — accept `ToolCall` JSON, return `ToolResult`
- [ ] **[P3]** Authentication / API key enforcement
- [ ] **[P3]** Agent SDK / client library for programmatic use

#### Tooling (P2)
- [ ] **[P2]** Configure ruff linter (`pyproject.toml`)
- [ ] **[P2]** Configure pytest (`pyproject.toml`)
- [ ] **[P2]** GitHub Actions CI — lint + test on push

---

## Out of Scope

<!-- Fill in: things this project intentionally will not do -->

---

## Open Questions

_All resolved._

| Question | Decision |
|---|---|
| REST gateway deployment target | Self-hosted (undecided timeline) |
| Canonical CLI entry point | `aegix_core/cli.py` — `aegix_cli/main.py` stub to be removed |
| Import path inconsistencies (`aegix.*` vs `aegix_core.*`) | Bug — fix as P1 |

---

## Changelog

| Date | Commit | What changed |
|---|---|---|
| 2026-03-15 | — | Initial SPEC.md drafted during kit adoption |
| 2026-03-15 | 9ca0c90 | Fix import paths: aegix.* → aegix_core.*, CLI entry point updated |
| 2026-03-15 | e06fbef | Remove empty aegix_cli stub; aegix_core/cli.py is now canonical CLI |
| 2026-03-15 | c8f8430 | Enforce resource limits (cpu, mem, pids, timeout) in DockerBackend |
| 2026-03-15 | 2246ad7 | Enforce network mode (none/bridge/host/allowlist) in DockerBackend |
| 2026-03-15 | b6eb660 | Enforce FS rules: read-only root, tmpfs write_paths, ro bind-mounts |
| 2026-03-15 | 4e49078 | PolicyEngine unit tests (18); fix r.research→r.search bug |
| 2026-03-15 | 7393f1e | ToolRouter unit tests (20) |
| 2026-03-15 | abab26d | DockerBackend integration tests (17); socket discovery for Rancher Desktop |
