from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from .integrations import build_integrations
from .models import ArtifactRecord, RunReceipt
from .policy import BiologyPolicy
from .security import canonical_json, sha256_file, sha256_text
from .tools import ToolRegistry
from .workspace import RunWorkspace


def _now() -> str:
    return datetime.now(UTC).isoformat()


class BioComputer:
    def __init__(
        self,
        workspace_root: str | Path = "runs",
        registry: ToolRegistry | None = None,
        policy: BiologyPolicy | None = None,
    ) -> None:
        self.workspace = RunWorkspace(workspace_root)
        self.registry = registry or ToolRegistry()
        self.policy = policy or BiologyPolicy()

    def execute(
        self,
        *,
        task: str,
        tool: str,
        payload: Mapping[str, Any],
        run_id: str | None = None,
    ) -> dict[str, Any]:
        run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        started_at = _now()
        decision = self.policy.evaluate(task, tool, payload)
        receipt = RunReceipt(
            run_id=run_id,
            task=task,
            tool=tool,
            status="blocked" if not decision.allowed else "running",
            started_at=started_at,
            policy=decision,
            input_digest=sha256_text(canonical_json(dict(payload))),
        )

        run_dir = self.workspace.create(run_id)
        input_path = self.workspace.write_json(
            run_dir,
            "input.json",
            {"task": task, "tool": tool, "payload": dict(payload)},
        )
        receipt.artifacts.append(
            ArtifactRecord(
                path="input.json",
                sha256=sha256_file(input_path),
                media_type="application/json",
                role="input",
            )
        )

        if decision.allowed:
            try:
                receipt.result = self.registry.run(tool, payload)
                receipt.status = "completed"
                result_path = self.workspace.write_json(run_dir, "result.json", receipt.result)
                receipt.artifacts.append(
                    ArtifactRecord(
                        path="result.json",
                        sha256=sha256_file(result_path),
                        media_type="application/json",
                        role="result",
                    )
                )
            except Exception as exc:
                receipt.status = "failed"
                receipt.error = f"{type(exc).__name__}: {exc}"

        receipt.completed_at = _now()
        receipt.integrations = build_integrations(receipt)
        self.workspace.write_json(run_dir, "receipt.json", receipt.to_dict())
        return receipt.to_dict()
