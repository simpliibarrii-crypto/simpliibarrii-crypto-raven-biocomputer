from __future__ import annotations

import os
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - optional dependency
    raise RuntimeError("Install raven-biocomputer[api] to run the API") from exc

from .executor import BioComputer

computer = BioComputer(workspace_root=os.getenv("RAVEN_BIOCOMPUTER_RUNS", "runs"))
app = FastAPI(
    title="Raven BioComputer",
    version="0.1.0",
    description="A guarded, auditable biology workstation for AI agents.",
)


class RunRequest(BaseModel):
    task: str = Field(min_length=3, max_length=2000)
    tool: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any]
    run_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "raven-biocomputer", "version": "0.1.0"}


@app.get("/v1/tools")
def list_tools() -> list[dict[str, Any]]:
    return computer.registry.list()


@app.post("/v1/runs")
def create_run(request: RunRequest) -> dict[str, Any]:
    try:
        return computer.execute(
            task=request.task,
            tool=request.tool,
            payload=request.payload,
            run_id=request.run_id,
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    try:
        return computer.workspace.read_receipt(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
