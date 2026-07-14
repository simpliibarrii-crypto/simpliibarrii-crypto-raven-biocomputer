from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    level: str
    reason: str
    requires_human_review: bool = False
    matched_rules: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["matched_rules"] = list(self.matched_rules)
        return data


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    sha256: str
    media_type: str
    role: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class RunReceipt:
    run_id: str
    task: str
    tool: str
    status: str
    started_at: str
    completed_at: str | None = None
    policy: PolicyDecision | None = None
    input_digest: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    artifacts: list[ArtifactRecord] = field(default_factory=list)
    error: str | None = None
    schema: str = "raven.biocomputer.run.v1"
    integrations: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "run_id": self.run_id,
            "task": self.task,
            "tool": self.tool,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "policy": self.policy.to_dict() if self.policy else None,
            "input_digest": self.input_digest,
            "result": self.result,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "error": self.error,
            "integrations": self.integrations,
        }
