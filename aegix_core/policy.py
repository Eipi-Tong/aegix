from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json, re, yaml

from aegix_core.models import (
    AdjustedPolicy, FSRule, Limits, NetworkMode, PolicyDecision, ToolCall, ToolContext
)

@dataclass(frozen=True)
class PolicyConfig:
    version: int = 1

    # commands
    deny_cmd_patterns: List[str] = field(default_factory=list)
    allow_cmd_patterns: List[str] = field(default_factory=list)

    # network
    network_mode: NetworkMode = "none"
    network_allowlist: List[str] = field(default_factory=list)

    # fs
    fs_rules: FSRule = field(default_factory=FSRule)

    # limits
    default_limits: Limits = field(default_factory=Limits)
    per_tool_limits: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # env
    env_allowlist: Optional[List[str]] = None  # None = allow all passed env keys (not recommended later)


def load_policy(path: str | Path) -> PolicyConfig:
    p = Path(path)
    data = yaml.safe_load(p.read_text()) or {}

    commands = data.get("commands", {}) or {}
    network = data.get("network", {}) or {}
    fs = data.get("fs", {}) or {}
    limits = data.get("limits", {}) or {}

    default_limits = limits.get("default", {}) or {}
    per_tool = limits.get("per_tool", {}) or {}

    cfg = PolicyConfig(
        version=int(data.get("version", 1)),
        deny_cmd_patterns=list(commands.get("deny_cmd_patterns", []) or []),
        allow_cmd_patterns=list(commands.get("allow_cmd_patterns", []) or []),
        network_mode=network.get("mode", "none"),
        network_allowlist=list(network.get("allowlist", []) or []),
        fs_rules=FSRule(
            write_paths=list(fs.get("write_paths", ["/workspace"]) or ["/workspace"]),
            read_only_paths=list(fs.get("read_only_paths", []) or []),
        ),
        default_limits=Limits(
            timeout_s=int(default_limits.get("timeout_s", 30)),
            cpu=float(default_limits.get("cpu", 1.0)),
            mem_mb=int(default_limits.get("mem_mb", 512)),
            pids=int(default_limits.get("pids", 256)),
        ),
        per_tool_limits=dict(per_tool),
        env_allowlist=data.get("env", {}).get("allowlist") if isinstance(data.get("env", {}), dict) else None,
    )
    _validate_policy(cfg)
    return cfg


def dump_effective_policy(cfg: PolicyConfig, out_path: str | Path) -> None:
    out = {
        "version": cfg.version,
        "commands": {
            "deny_cmd_patterns": cfg.deny_cmd_patterns,
            "allow_cmd_patterns": cfg.allow_cmd_patterns,
        },
        "network": {
            "mode": cfg.network_mode,
            "allowlist": cfg.network_allowlist,
        },
        "fs": {
            "write_paths": cfg.fs_rules.write_paths,
            "read_only_paths": cfg.fs_rules.read_only_paths,
        },
        "limits": {
            "default": cfg.default_limits.__dict__,
            "per_tool": cfg.per_tool_limits,
        },
        "env": {
            "allowlist": cfg.env_allowlist,
        },
    }
    Path(out_path).write_text(json.dumps(out, indent=2, sort_keys=True))


def _validate_policy(cfg: PolicyConfig) -> None:
    if cfg.network_mode not in ("none", "bridge", "host", "allowlist"):
        raise ValueError(f"Invalid network_mode: {cfg.network_mode}")
    # regex compile check (fail fast)
    for pattern in cfg.deny_cmd_patterns + cfg.allow_cmd_patterns:
        re.compile(pattern)


class PolicyEngine:
    def __init__(self, cfg: PolicyConfig):
        self.cfg = cfg
        self._deny_res = [re.compile(p) for p in cfg.deny_cmd_patterns]
        self._allow_res = [re.compile(p) for p in cfg.allow_cmd_patterns] if cfg.allow_cmd_patterns else []
    
    def evaluate(self, call: ToolCall, ctx: ToolContext) -> PolicyDecision:
        limits = self.cfg.default_limits.merged(self.cfg.per_tool_limits.get(call.tool_name))
        
        adjusted = AdjustedPolicy(
            limits=limits,
            network_mode=self.cfg.network_mode,
            env_allowlist=self.cfg.env_allowlist,
            fs_rules=self.cfg.fs_rules,
        )

        for r in self._deny_res:
            if r.search(call.cmd or ""):
                return PolicyDecision(
                    allow=False,
                    reason=f"Denied by pattern: {r.pattern}",
                    adjusted=adjusted,
                    redactions={},
                )
        
        if self._allow_res:
            ok = any(r.research(call.cmd or "") for r in self._allow_res)
            if not ok:
                return PolicyDecision(
                    allow=False,
                    reason="Denied: command not in allowlist",
                    adjusted=adjusted,
                    redactions={},
                )
        
        if self.cfg.network_mode == "allowlist" and not self.cfg.network_allowlist:
            return PolicyDecision(
                allow=False,
                reason="Denied: network allowlist mode but allowlist is empty",
                adjusted=adjusted,
                redactions={},
            )
        
        return PolicyDecision(
            allow=True,
            reason="Allowed",
            adjusted=adjusted,
            redactions={},
        )
