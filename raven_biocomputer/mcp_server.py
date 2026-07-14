from __future__ import annotations

import os
from typing import Any

from .executor import BioComputer

computer = BioComputer(workspace_root=os.getenv("RAVEN_BIOCOMPUTER_RUNS", "runs"))


def create_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install raven-biocomputer[mcp] to run the MCP server") from exc

    server = FastMCP("Raven BioComputer")

    @server.tool()
    def list_biology_tools() -> list[dict[str, Any]]:
        """List bounded dry-lab tools available in Raven BioComputer."""
        return computer.registry.list()

    @server.tool()
    def run_biology_tool(task: str, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a bounded biology tool and return an auditable Raven receipt."""
        return computer.execute(task=task, tool=tool, payload=payload)

    @server.resource("raven-biocomputer://runs/{run_id}")
    def read_run(run_id: str) -> dict[str, Any]:
        """Read a completed Raven BioComputer receipt by run identifier."""
        return computer.workspace.read_receipt(run_id)

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
