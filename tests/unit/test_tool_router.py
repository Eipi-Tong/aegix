"""Unit tests for ToolRouter.handle().

DockerBackend is mocked so no Docker daemon is required.
AuditLogger and ArtifactWriter use real implementations pointed at tmp_path.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aegix_core.errors import AegixError
from aegix_core.io.artifacts import ArtifactWriter
from aegix_core.logging.audit import AuditLogger
from aegix_core.models import (
    AdjustedPolicy, FSRule, Limits, PolicyDecision, ToolCall, ToolContext,
)
from aegix_core.policy import PolicyConfig, PolicyEngine
from aegix_core.router import ToolResult, ToolRouter
from aegix_core.runtime.docker_backend import DockerBackend, ExecResult
from tests.conftest import make_call, make_ctx, make_fs_rules, make_limits


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_CONTAINER_ID = "abc123container"


def _adjusted(limits: Limits | None = None) -> AdjustedPolicy:
    return AdjustedPolicy(
        limits=limits or make_limits(),
        network_mode="none",
        env_allowlist=None,
        fs_rules=make_fs_rules(),
    )


def _allow_decision(limits: Limits | None = None) -> PolicyDecision:
    return PolicyDecision(allow=True, reason="Allowed", adjusted=_adjusted(limits))


def _deny_decision(reason: str = "Denied by pattern: test") -> PolicyDecision:
    return PolicyDecision(allow=False, reason=reason, adjusted=_adjusted())


@pytest.fixture()
def run_dir(tmp_path: Path) -> Path:
    d = tmp_path / "runs" / "run-001"
    d.mkdir(parents=True)
    return d


@pytest.fixture()
def auditor(tmp_path: Path) -> AuditLogger:
    return AuditLogger(events_path=tmp_path / "events.jsonl")


@pytest.fixture()
def artifacts(run_dir: Path) -> ArtifactWriter:
    return ArtifactWriter(run_dir=run_dir)


@pytest.fixture()
def mock_backend() -> MagicMock:
    backend = MagicMock(spec=DockerBackend)
    backend.create.return_value = FAKE_CONTAINER_ID
    backend.exec.return_value = ExecResult(stdout="hello\n", stderr="", exit_code=0)
    return backend


@pytest.fixture()
def mock_policy() -> MagicMock:
    policy = MagicMock(spec=PolicyEngine)
    policy.evaluate.return_value = _allow_decision()
    return policy


@pytest.fixture()
def router(mock_policy, mock_backend, auditor, artifacts) -> ToolRouter:
    return ToolRouter(
        policy_engine=mock_policy,
        backend=mock_backend,
        auditor=auditor,
        artifacts=artifacts,
    )


# ---------------------------------------------------------------------------
# Validation error tests
# ---------------------------------------------------------------------------

class TestValidation:
    def test_missing_tool_name_returns_invalid_tool_call(self, router, run_dir):
        call = ToolCall(tool_name="", cmd="echo hi")
        result = router.handle(call, make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "INVALID_TOOL_CALL"
        assert "tool_name" in result.error.message

    def test_missing_cmd_returns_invalid_tool_call(self, router, run_dir):
        call = ToolCall(tool_name="bash", cmd="")
        result = router.handle(call, make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "INVALID_TOOL_CALL"
        assert "cmd" in result.error.message

    def test_whitespace_only_cmd_returns_invalid_tool_call(self, router, run_dir):
        call = ToolCall(tool_name="bash", cmd="   ")
        result = router.handle(call, make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "INVALID_TOOL_CALL"

    def test_backend_not_called_on_validation_error(self, router, mock_backend, run_dir):
        call = ToolCall(tool_name="bash", cmd="")
        router.handle(call, make_ctx(), run_dir)
        mock_backend.create.assert_not_called()


# ---------------------------------------------------------------------------
# Policy deny tests
# ---------------------------------------------------------------------------

class TestPolicyDeny:
    def test_policy_deny_returns_denied_policy_error(
        self, router, mock_policy, run_dir
    ):
        mock_policy.evaluate.return_value = _deny_decision("Denied by pattern: sudo")
        result = router.handle(make_call(cmd="sudo ls"), make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "DENIED_POLICY"
        assert "sudo" in result.error.message

    def test_backend_not_called_on_policy_deny(
        self, router, mock_policy, mock_backend, run_dir
    ):
        mock_policy.evaluate.return_value = _deny_decision()
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.create.assert_not_called()


# ---------------------------------------------------------------------------
# Exec success tests
# ---------------------------------------------------------------------------

class TestExecSuccess:
    def test_successful_exec_returns_ok_true(self, router, run_dir):
        result = router.handle(make_call(cmd="echo hello"), make_ctx(), run_dir)
        assert result.ok is True
        assert result.error is None

    def test_exec_result_attached_on_success(self, router, run_dir):
        result = router.handle(make_call(), make_ctx(), run_dir)
        assert result.exec_result is not None
        assert result.exec_result.stdout == "hello\n"
        assert result.exec_result.exit_code == 0

    def test_backend_create_called_with_limits_from_policy(
        self, router, mock_policy, mock_backend, run_dir
    ):
        limits = make_limits(timeout_s=10, cpu=0.5, mem_mb=256, pids=64)
        mock_policy.evaluate.return_value = _allow_decision(limits)
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.create.assert_called_once()
        _, kwargs = mock_backend.create.call_args
        assert kwargs["limits"] == limits

    def test_backend_exec_called_with_timeout_from_policy(
        self, router, mock_policy, mock_backend, run_dir
    ):
        limits = make_limits(timeout_s=15)
        mock_policy.evaluate.return_value = _allow_decision(limits)
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.exec.assert_called_once()
        _, kwargs = mock_backend.exec.call_args
        assert kwargs["timeout_s"] == 15

    def test_artifacts_written_on_success(self, router, run_dir):
        router.handle(make_call(), make_ctx(), run_dir)
        assert (run_dir / "stdout.txt").read_text() == "hello\n"
        assert (run_dir / "exit_code.txt").read_text() == "0\n"


# ---------------------------------------------------------------------------
# Exec failure tests
# ---------------------------------------------------------------------------

class TestExecFailure:
    def test_nonzero_exit_returns_ok_false(self, router, mock_backend, run_dir):
        mock_backend.exec.return_value = ExecResult(
            stdout="", stderr="error!", exit_code=1
        )
        result = router.handle(make_call(), make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "NONZERO_EXIT"
        assert result.error.exit_code == 1

    def test_nonzero_exit_attaches_exec_result(self, router, mock_backend, run_dir):
        mock_backend.exec.return_value = ExecResult(
            stdout="", stderr="oops", exit_code=2
        )
        result = router.handle(make_call(), make_ctx(), run_dir)
        assert result.exec_result is not None
        assert result.exec_result.exit_code == 2

    def test_timeout_error_returns_timeout_type(self, router, mock_backend, run_dir):
        mock_backend.exec.side_effect = TimeoutError("Command exceeded timeout of 30s")
        result = router.handle(make_call(), make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "TIMEOUT"
        assert "30s" in result.error.message

    def test_backend_exception_returns_backend_error(
        self, router, mock_backend, run_dir
    ):
        mock_backend.exec.side_effect = RuntimeError("docker daemon not running")
        result = router.handle(make_call(), make_ctx(), run_dir)
        assert result.ok is False
        assert result.error.type == "BACKEND_ERROR"
        assert "RuntimeError" in result.error.message


# ---------------------------------------------------------------------------
# Container cleanup tests
# ---------------------------------------------------------------------------

class TestContainerCleanup:
    def test_destroy_called_after_successful_exec(
        self, router, mock_backend, run_dir
    ):
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.destroy.assert_called_once_with(FAKE_CONTAINER_ID)

    def test_destroy_called_after_nonzero_exit(
        self, router, mock_backend, run_dir
    ):
        mock_backend.exec.return_value = ExecResult("", "err", exit_code=1)
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.destroy.assert_called_once_with(FAKE_CONTAINER_ID)

    def test_destroy_called_after_timeout(self, router, mock_backend, run_dir):
        mock_backend.exec.side_effect = TimeoutError("timed out")
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.destroy.assert_called_once_with(FAKE_CONTAINER_ID)

    def test_destroy_called_after_backend_error(
        self, router, mock_backend, run_dir
    ):
        mock_backend.exec.side_effect = RuntimeError("crash")
        router.handle(make_call(), make_ctx(), run_dir)
        mock_backend.destroy.assert_called_once_with(FAKE_CONTAINER_ID)

    def test_destroy_not_called_if_container_never_created(
        self, router, mock_backend, run_dir
    ):
        """Validation fails before create() — no container to destroy."""
        call = ToolCall(tool_name="bash", cmd="")
        router.handle(call, make_ctx(), run_dir)
        mock_backend.destroy.assert_not_called()
