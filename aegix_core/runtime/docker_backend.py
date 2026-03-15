from __future__ import annotations

from dataclasses import dataclass
import docker

from aegix_core.models import Limits


@dataclass(frozen=True)
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int


class DockerBackend:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def create(self, image: str, limits: Limits) -> str:
        """Create a detached container with resource limits applied."""
        container = self.client.containers.run(
            image=image,
            command=["sh", "-lc", "tail -f /dev/null"],
            detach=True,
            tty=True,
            # CPU: nano_cpus = cores * 1e9 (e.g. 1.0 CPU = 1_000_000_000)
            nano_cpus=int(limits.cpu * 1_000_000_000),
            # Memory: Docker accepts strings like "512m"
            mem_limit=f"{limits.mem_mb}m",
            # PID limit
            pids_limit=limits.pids,
        )
        return container.id

    def exec(self, container_id: str, cmd: str, timeout_s: int) -> ExecResult:
        """Execute a command inside the container, enforcing a wall-clock timeout.

        Uses the POSIX `timeout` utility inside the container:
          timeout -k <kill_grace> <timeout_s> sh -lc <cmd>
        Exit code 124 from `timeout` means the time limit was exceeded.
        """
        container = self.client.containers.get(container_id)

        # Wrap with timeout; kill grace period = 5 s after SIGTERM
        wrapped = ["timeout", "-k", "5", str(timeout_s), "sh", "-lc", cmd]
        res = container.exec_run(wrapped, demux=True)
        exit_code = int(res.exit_code)

        if exit_code == 124:
            raise TimeoutError(
                f"Command exceeded timeout of {timeout_s}s"
            )

        stdout_b, stderr_b = (
            res.output if isinstance(res.output, tuple) else (res.output, b"")
        )
        return ExecResult(
            stdout=(stdout_b or b"").decode("utf-8", errors="replace"),
            stderr=(stderr_b or b"").decode("utf-8", errors="replace"),
            exit_code=exit_code,
        )

    def destroy(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.stop()
        container.remove(force=True)
