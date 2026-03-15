"""Shared pytest fixtures and configuration."""
from __future__ import annotations

import pytest

from aegix_core.models import FSRule, Limits, ToolCall, ToolContext


# ---------------------------------------------------------------------------
# Reusable model factories
# ---------------------------------------------------------------------------

def make_call(
    tool_name: str = "bash",
    cmd: str = "echo hello",
    image: str | None = None,
) -> ToolCall:
    return ToolCall(tool_name=tool_name, cmd=cmd, image=image)


def make_ctx(run_id: str = "test-run-001") -> ToolContext:
    return ToolContext(run_id=run_id)


def make_limits(**overrides) -> Limits:
    defaults = dict(timeout_s=30, cpu=1.0, mem_mb=512, pids=256)
    defaults.update(overrides)
    return Limits(**defaults)


def make_fs_rules(
    write_paths: list[str] | None = None,
    read_only_paths: list[str] | None = None,
) -> FSRule:
    return FSRule(
        write_paths=write_paths or ["/workspace"],
        read_only_paths=read_only_paths or [],
    )
