"""Unit tests for PolicyEngine.evaluate()."""
from __future__ import annotations

import pytest

from aegix_core.models import FSRule, Limits, ToolCall, ToolContext
from aegix_core.policy import PolicyConfig, PolicyEngine
from tests.conftest import make_call, make_ctx, make_limits


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_engine(
    deny_cmd_patterns: list[str] | None = None,
    allow_cmd_patterns: list[str] | None = None,
    network_mode: str = "none",
    network_allowlist: list[str] | None = None,
    per_tool_limits: dict | None = None,
    default_limits: Limits | None = None,
) -> PolicyEngine:
    cfg = PolicyConfig(
        deny_cmd_patterns=deny_cmd_patterns or [],
        allow_cmd_patterns=allow_cmd_patterns or [],
        network_mode=network_mode,
        network_allowlist=network_allowlist or [],
        per_tool_limits=per_tool_limits or {},
        default_limits=default_limits or make_limits(),
    )
    return PolicyEngine(cfg)


# ---------------------------------------------------------------------------
# Deny pattern tests
# ---------------------------------------------------------------------------

class TestDenyPatterns:
    def test_command_matching_deny_pattern_is_blocked(self):
        engine = make_engine(deny_cmd_patterns=[r"(?i)\bsudo\b"])
        result = engine.evaluate(make_call(cmd="sudo rm -rf /"), make_ctx())
        assert result.allow is False
        assert "sudo" in result.reason.lower()

    def test_command_not_matching_deny_pattern_is_allowed(self):
        engine = make_engine(deny_cmd_patterns=[r"(?i)\bsudo\b"])
        result = engine.evaluate(make_call(cmd="echo hello"), make_ctx())
        assert result.allow is True

    def test_deny_pattern_is_case_insensitive(self):
        engine = make_engine(deny_cmd_patterns=[r"(?i)\bsudo\b"])
        for variant in ("SUDO ls", "Sudo ls", "sUdO ls"):
            result = engine.evaluate(make_call(cmd=variant), make_ctx())
            assert result.allow is False, f"Expected deny for: {variant!r}"

    def test_first_matching_deny_pattern_wins(self):
        engine = make_engine(deny_cmd_patterns=[r"(?i)\bsudo\b", r"(?i)\bssh\b"])
        result = engine.evaluate(make_call(cmd="sudo ssh root@host"), make_ctx())
        assert result.allow is False
        assert "sudo" in result.reason

    def test_no_deny_patterns_allows_any_command(self):
        engine = make_engine(deny_cmd_patterns=[])
        result = engine.evaluate(make_call(cmd="rm -rf /"), make_ctx())
        assert result.allow is True

    def test_deny_reason_contains_pattern(self):
        pattern = r"(?i)\bcurl\b"
        engine = make_engine(deny_cmd_patterns=[pattern])
        result = engine.evaluate(make_call(cmd="curl http://example.com"), make_ctx())
        assert result.allow is False
        assert pattern in result.reason


# ---------------------------------------------------------------------------
# Allow-list mode tests
# ---------------------------------------------------------------------------

class TestAllowListMode:
    def test_command_matching_allow_pattern_is_permitted(self):
        engine = make_engine(allow_cmd_patterns=[r"^echo\b"])
        result = engine.evaluate(make_call(cmd="echo hello"), make_ctx())
        assert result.allow is True

    def test_command_not_matching_allow_pattern_is_blocked(self):
        engine = make_engine(allow_cmd_patterns=[r"^echo\b"])
        result = engine.evaluate(make_call(cmd="ls -la"), make_ctx())
        assert result.allow is False
        assert "allowlist" in result.reason.lower()

    def test_deny_takes_priority_over_allow(self):
        """A command matching both deny and allow patterns must be denied."""
        engine = make_engine(
            deny_cmd_patterns=[r"(?i)\bsudo\b"],
            allow_cmd_patterns=[r"sudo"],
        )
        result = engine.evaluate(make_call(cmd="sudo echo hi"), make_ctx())
        assert result.allow is False

    def test_empty_allow_patterns_does_not_activate_allowlist_mode(self):
        """allow_cmd_patterns=[] means no allowlist — all non-denied commands pass."""
        engine = make_engine(allow_cmd_patterns=[])
        result = engine.evaluate(make_call(cmd="ls -la"), make_ctx())
        assert result.allow is True


# ---------------------------------------------------------------------------
# Network allowlist guard
# ---------------------------------------------------------------------------

class TestNetworkAllowlistGuard:
    def test_allowlist_mode_with_empty_allowlist_is_denied(self):
        engine = make_engine(network_mode="allowlist", network_allowlist=[])
        result = engine.evaluate(make_call(cmd="echo ok"), make_ctx())
        assert result.allow is False
        assert "allowlist" in result.reason.lower()

    def test_allowlist_mode_with_entries_is_allowed(self):
        engine = make_engine(
            network_mode="allowlist",
            network_allowlist=["api.example.com"],
        )
        result = engine.evaluate(make_call(cmd="echo ok"), make_ctx())
        assert result.allow is True

    def test_bridge_mode_does_not_require_allowlist(self):
        engine = make_engine(network_mode="bridge", network_allowlist=[])
        result = engine.evaluate(make_call(cmd="echo ok"), make_ctx())
        assert result.allow is True

    def test_none_mode_does_not_require_allowlist(self):
        engine = make_engine(network_mode="none", network_allowlist=[])
        result = engine.evaluate(make_call(cmd="echo ok"), make_ctx())
        assert result.allow is True


# ---------------------------------------------------------------------------
# Per-tool limit merging
# ---------------------------------------------------------------------------

class TestPerToolLimits:
    def test_per_tool_limits_override_defaults(self):
        engine = make_engine(
            default_limits=make_limits(timeout_s=30, mem_mb=512),
            per_tool_limits={"bash": {"timeout_s": 20, "mem_mb": 768}},
        )
        result = engine.evaluate(make_call(tool_name="bash", cmd="echo hi"), make_ctx())
        assert result.allow is True
        assert result.adjusted.limits.timeout_s == 20
        assert result.adjusted.limits.mem_mb == 768

    def test_per_tool_limits_partial_override(self):
        """Only specified keys are overridden; others retain default values."""
        engine = make_engine(
            default_limits=make_limits(timeout_s=30, cpu=1.0, mem_mb=512, pids=256),
            per_tool_limits={"python": {"timeout_s": 45}},
        )
        result = engine.evaluate(make_call(tool_name="python", cmd="print('hi')"), make_ctx())
        assert result.adjusted.limits.timeout_s == 45
        assert result.adjusted.limits.cpu == 1.0
        assert result.adjusted.limits.mem_mb == 512
        assert result.adjusted.limits.pids == 256

    def test_unknown_tool_uses_default_limits(self):
        engine = make_engine(
            default_limits=make_limits(timeout_s=30),
            per_tool_limits={"bash": {"timeout_s": 10}},
        )
        result = engine.evaluate(make_call(tool_name="unknown_tool", cmd="echo hi"), make_ctx())
        assert result.adjusted.limits.timeout_s == 30

    def test_adjusted_policy_carries_correct_network_and_fs(self):
        engine = make_engine(network_mode="bridge")
        result = engine.evaluate(make_call(cmd="echo hi"), make_ctx())
        assert result.adjusted.network_mode == "bridge"
        assert isinstance(result.adjusted.fs_rules, FSRule)
