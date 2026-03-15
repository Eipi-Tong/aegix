from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import time
import uuid

from aegix_core.io.artifacts import ArtifactWriter
from aegix_core.logging.audit import AuditLogger
from aegix_core.runtime.docker_backend import DockerBackend, ExecResult

# from aegix_core.models import ToolCall, ToolContext
from aegix_core.policy import PolicyEngine
from aegix_core.errors import AegixError


@dataclass
class ToolResult:
    ok: bool
    exec_result: Optional[ExecResult] = None
    error: Optional[AegixError] = None


class ToolRouter:
    def __init__(self, policy_engine: PolicyEngine, backend: DockerBackend, auditor: AuditLogger, artifacts: ArtifactWriter, default_image: str = "python:3.11-slim"):
        self.policy = policy_engine
        self.backend = backend
        self.auditor = auditor
        self.artifacts = artifacts
        self.default_image = default_image

    def handle(self, call, ctx, run_dir: Path) -> ToolResult:
        run_id = getattr(ctx, "run_id", None)

        self.auditor.log("RUN_START", {
            "run_id": run_id,
            "tool_name": getattr(call, "tool_name", None),
        })

        # ---------- VALIDATION ----------
        err = self._validate(call)
        if err:
            self.auditor.log("VALIDATION_ERROR", {"run_id": run_id, "error": err.__dict__})
            self._write_report(ctx, call, ok=False, error=err)
            self.auditor.log("RUN_END", {"run_id": run_id, "ok": False, "error_type": err.type})
            return ToolResult(ok=False, error=err)

        # ---------- POLICY ----------
        decision = self.policy.evaluate(call, ctx)

        self.auditor.log("POLICY_EVALUATED", {
            "run_id": run_id,
            "allow": decision.allow,
            "reason": decision.reason,
        })

        if not decision.allow:
            err = AegixError(
                type="DENIED_POLICY",
                message=decision.reason,
            )
            self.auditor.log("POLICY_DENY", {"run_id": run_id, "reason": decision.reason})
            self._write_report(ctx, call, ok=False, error=err, policy_reason=decision.reason)
            self.auditor.log("RUN_END", {"run_id": run_id, "ok": False, "error_type": err.type})
            return ToolResult(ok=False, error=err)

        self.auditor.log("POLICY_ALLOW", {"run_id": run_id, "reason": decision.reason})

        # ---------- EXEC ----------
        container_id: Optional[str] = None
        try:
            image = getattr(call, "image", None) or self.default_image

            self.auditor.log("SANDBOX_CREATE_START", {"run_id": run_id, "image": image})
            container_id = self.backend.create(
                image=image,
                limits=decision.adjusted.limits,
                network_mode=decision.adjusted.network_mode,
            )
            self.auditor.log("SANDBOX_CREATE_END", {"run_id": run_id, "container_id": container_id})

            self.auditor.log("EXEC_START", {
                "run_id": run_id,
                "container_id": container_id,
                "cmd": getattr(call, "cmd", ""),
            })

            res = self.backend.exec(
                container_id=container_id,
                cmd=getattr(call, "cmd", ""),
                timeout_s=decision.adjusted.limits.timeout_s,
            )

            self.auditor.log("EXEC_END", {
                "run_id": run_id,
                "container_id": container_id,
                "exit_code": res.exit_code,
                "stdout_len": len(res.stdout or ""),
                "stderr_len": len(res.stderr or ""),
            })

            # artifacts
            self.artifacts.write_text("stdout.txt", res.stdout or "")
            self.artifacts.write_text("stderr.txt", res.stderr or "")
            self.artifacts.write_text("exit_code.txt", f"{res.exit_code}\n")

            if res.exit_code != 0:
                err = AegixError(
                    type="NONZERO_EXIT",
                    message="Command exited with non-zero status",
                    exit_code=res.exit_code,
                )
                self._write_report(ctx, call, ok=False, error=err, exec_result=res, policy_reason=decision.reason)
                self.auditor.log("RUN_END", {"run_id": run_id, "ok": False, "exit_code": res.exit_code})
                return ToolResult(ok=False, exec_result=res, error=err)

            self._write_report(ctx, call, ok=True, exec_result=res, policy_reason=decision.reason)
            self.auditor.log("RUN_END", {"run_id": run_id, "ok": True, "exit_code": res.exit_code})
            return ToolResult(ok=True, exec_result=res)

        except TimeoutError as e:
            err = AegixError(
                type="TIMEOUT",
                message=str(e),
            )
            self.auditor.log("EXEC_TIMEOUT", {"run_id": run_id, "message": str(e)})
            self._write_report(ctx, call, ok=False, error=err)
            self.auditor.log("RUN_END", {"run_id": run_id, "ok": False, "error_type": err.type})
            return ToolResult(ok=False, error=err)

        except Exception as e:
            err = AegixError(
                type="BACKEND_ERROR",
                message=f"{type(e).__name__}: {e}",
            )
            self.auditor.log("BACKEND_ERROR", {"run_id": run_id, "message": err.message})
            self._write_report(ctx, call, ok=False, error=err)
            self.auditor.log("RUN_END", {"run_id": run_id, "ok": False, "error_type": err.type})
            return ToolResult(ok=False, error=err)

        finally:
            if container_id:
                try:
                    self.auditor.log("SANDBOX_DESTROY_START", {
                        "run_id": run_id,
                        "container_id": container_id,
                    })
                    self.backend.destroy(container_id)
                    self.auditor.log("SANDBOX_DESTROY_END", {
                        "run_id": run_id,
                        "container_id": container_id,
                    })
                except Exception as e:
                    self.auditor.log("SANDBOX_DESTROY_FAILED", {
                        "run_id": run_id,
                        "container_id": container_id,
                        "message": f"{type(e).__name__}: {e}",
                    })

    # ---------------- helpers ----------------

    def _validate(self, call) -> Optional[AegixError]:
        if not getattr(call, "tool_name", None):
            return AegixError("INVALID_TOOL_CALL", "tool_name is required")

        if not getattr(call, "cmd", None) or not str(call.cmd).strip():
            return AegixError("INVALID_TOOL_CALL", "cmd is required")

        return None

    def _write_report(
        self,
        ctx,
        call,
        ok: bool,
        error: Optional[AegixError] = None,
        exec_result: Optional[ExecResult] = None,
        policy_reason: Optional[str] = None,
    ) -> None:
        report: Dict[str, Any] = {
            "run_id": getattr(ctx, "run_id", None),
            "ok": ok,
            "tool": {
                "tool_name": getattr(call, "tool_name", None),
                "image": getattr(call, "image", None) or self.default_image,
                "cmd": getattr(call, "cmd", None),
            },
            "policy": {"reason": policy_reason},
        }

        if exec_result is not None:
            report["exec"] = {
                "exit_code": exec_result.exit_code,
                "stdout_len": len(exec_result.stdout or ""),
                "stderr_len": len(exec_result.stderr or ""),
            }

        if error is not None:
            report["error"] = {
                "type": error.type,
                "message": error.message,
                "exit_code": error.exit_code,
            }

        self.artifacts.write_text("report.json", self.artifacts.json_dumps(report))