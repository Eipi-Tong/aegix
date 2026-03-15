"""Integration tests for DockerBackend.

Requires a running Docker daemon. Mark: pytest -m integration
Skip with: pytest -m "not integration"

Image used: python:3.11-slim (pulled on first run).
"""
from __future__ import annotations

import pytest

from aegix_core.models import FSRule, Limits, NetworkMode
from aegix_core.runtime.docker_backend import DockerBackend

pytestmark = pytest.mark.integration

IMAGE = "python:3.11-slim"


def _default_limits(**overrides) -> Limits:
    base = dict(timeout_s=30, cpu=1.0, mem_mb=512, pids=256)
    base.update(overrides)
    return Limits(**base)


def _default_fs() -> FSRule:
    return FSRule(write_paths=["/workspace", "/tmp"], read_only_paths=[])


def _create(backend: DockerBackend, container_ids: list, **limit_overrides) -> str:
    """Helper: create a container, register it for cleanup, return its id."""
    cid = backend.create(
        image=IMAGE,
        limits=_default_limits(**limit_overrides),
        network_mode="none",
        fs_rules=_default_fs(),
    )
    container_ids.append(cid)
    return cid


# ---------------------------------------------------------------------------
# create / destroy
# ---------------------------------------------------------------------------

class TestCreateDestroy:
    def test_create_returns_nonempty_container_id(self, backend, container_ids):
        cid = _create(backend, container_ids)
        assert isinstance(cid, str) and len(cid) > 0

    def test_created_container_is_running(self, backend, container_ids):
        cid = _create(backend, container_ids)
        container = backend.client.containers.get(cid)
        assert container.status == "running"

    def test_destroy_removes_container(self, backend, container_ids):
        cid = _create(backend, container_ids)
        backend.destroy(cid)
        container_ids.remove(cid)  # already destroyed; skip cleanup fixture
        import docker as docker_sdk
        from docker.errors import NotFound
        with pytest.raises(NotFound):
            backend.client.containers.get(cid)


# ---------------------------------------------------------------------------
# exec
# ---------------------------------------------------------------------------

class TestExec:
    def test_exec_captures_stdout(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "echo hello", timeout_s=10)
        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_exec_captures_stderr(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "echo errormsg >&2", timeout_s=10)
        assert "errormsg" in result.stderr

    def test_exec_captures_nonzero_exit_code(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "exit 42", timeout_s=10)
        assert result.exit_code == 42

    def test_exec_multiline_output(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "printf 'line1\\nline2\\nline3\\n'", timeout_s=10)
        assert result.exit_code == 0
        lines = result.stdout.strip().splitlines()
        assert lines == ["line1", "line2", "line3"]

    def test_exec_timeout_raises_timeout_error(self, backend, container_ids):
        cid = _create(backend, container_ids)
        with pytest.raises(TimeoutError, match="timeout"):
            backend.exec(cid, "sleep 60", timeout_s=2)

    def test_exec_sequential_commands_in_same_container(self, backend, container_ids):
        """Multiple execs in the same container should all succeed."""
        cid = _create(backend, container_ids)
        r1 = backend.exec(cid, "echo first", timeout_s=10)
        r2 = backend.exec(cid, "echo second", timeout_s=10)
        assert "first" in r1.stdout
        assert "second" in r2.stdout


# ---------------------------------------------------------------------------
# Resource limits applied to container
# ---------------------------------------------------------------------------

class TestResourceLimits:
    def test_container_created_with_mem_limit(self, backend, container_ids):
        cid = _create(backend, container_ids, mem_mb=256)
        container = backend.client.containers.get(cid)
        container.reload()
        host_config = container.attrs["HostConfig"]
        # Docker stores mem_limit in bytes
        assert host_config["Memory"] == 256 * 1024 * 1024

    def test_container_created_with_pids_limit(self, backend, container_ids):
        cid = _create(backend, container_ids, pids=64)
        container = backend.client.containers.get(cid)
        container.reload()
        assert container.attrs["HostConfig"]["PidsLimit"] == 64

    def test_container_created_with_nano_cpus(self, backend, container_ids):
        cid = _create(backend, container_ids, cpu=0.5)
        container = backend.client.containers.get(cid)
        container.reload()
        assert container.attrs["HostConfig"]["NanoCpus"] == int(0.5 * 1_000_000_000)


# ---------------------------------------------------------------------------
# Network mode
# ---------------------------------------------------------------------------

class TestNetworkMode:
    def test_none_network_mode_has_no_network(self, backend, container_ids):
        cid = backend.create(
            image=IMAGE,
            limits=_default_limits(),
            network_mode="none",
            fs_rules=_default_fs(),
        )
        container_ids.append(cid)
        container = backend.client.containers.get(cid)
        container.reload()
        net_mode = container.attrs["HostConfig"]["NetworkMode"]
        assert net_mode == "none"

    def test_bridge_network_mode(self, backend, container_ids):
        cid = backend.create(
            image=IMAGE,
            limits=_default_limits(),
            network_mode="bridge",
            fs_rules=_default_fs(),
        )
        container_ids.append(cid)
        container = backend.client.containers.get(cid)
        container.reload()
        net_mode = container.attrs["HostConfig"]["NetworkMode"]
        assert net_mode == "bridge"


# ---------------------------------------------------------------------------
# FS rules
# ---------------------------------------------------------------------------

class TestFSRules:
    def test_workspace_is_writable(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "echo data > /workspace/test.txt && cat /workspace/test.txt", timeout_s=10)
        assert result.exit_code == 0
        assert "data" in result.stdout

    def test_root_filesystem_is_read_only(self, backend, container_ids):
        """Writes outside of tmpfs-mounted paths should fail."""
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "touch /readonly_test.txt", timeout_s=10)
        assert result.exit_code != 0

    def test_tmp_is_writable(self, backend, container_ids):
        cid = _create(backend, container_ids)
        result = backend.exec(cid, "echo ok > /tmp/test.txt && cat /tmp/test.txt", timeout_s=10)
        assert result.exit_code == 0
        assert "ok" in result.stdout
