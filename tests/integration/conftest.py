"""Integration test fixtures for DockerBackend.

These tests require a running Docker daemon.
Skip them with: pytest -m "not integration"
"""
from __future__ import annotations

import os
from pathlib import Path

import docker as docker_sdk
import pytest

from aegix_core.runtime.docker_backend import DockerBackend

# Known socket locations to try in order
_CANDIDATE_SOCKETS = [
    os.environ.get("DOCKER_HOST"),               # explicit env override
    "unix:///var/run/docker.sock",               # standard Linux / Docker Desktop
    f"unix://{Path.home()}/.rd/docker.sock",     # Rancher Desktop (macOS)
    f"unix://{Path.home()}/.docker/run/docker.sock",  # Docker Desktop (macOS alt)
]


def _find_docker_client() -> docker_sdk.DockerClient | None:
    """Return the first reachable Docker client, or None."""
    for url in _CANDIDATE_SOCKETS:
        if not url:
            continue
        try:
            client = docker_sdk.DockerClient(base_url=url)
            client.ping()
            return client
        except Exception:
            continue
    return None


@pytest.fixture(scope="session")
def docker_client() -> docker_sdk.DockerClient | None:
    return _find_docker_client()


@pytest.fixture(scope="session")
def backend(docker_client) -> DockerBackend:
    if docker_client is None:
        pytest.skip("No reachable Docker daemon found")
    return DockerBackend(client=docker_client)


@pytest.fixture()
def container_ids() -> list[str]:
    """Accumulate container IDs for cleanup after each test."""
    return []


@pytest.fixture(autouse=True)
def cleanup_containers(backend, container_ids):
    """Destroy any containers created during a test, even if it fails."""
    yield
    for cid in container_ids:
        try:
            backend.destroy(cid)
        except Exception:
            pass
