from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .executor import BioComputer


def _load_payload(raw: str) -> dict:
    if raw.startswith("@"):
        return json.loads(Path(raw[1:]).read_text(encoding="utf-8"))
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("payload must decode to a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="raven-biocomputer",
        description="Run bounded biology tools inside auditable workspaces.",
    )
    parser.add_argument("--workspace", default="runs", help="workspace root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("tools", help="list available deterministic tools")

    run = subparsers.add_parser("run", help="execute one bounded biology tool")
    run.add_argument("tool")
    run.add_argument("--task", required=True)
    run.add_argument("--payload", required=True, help="JSON object or @path/to/file.json")
    run.add_argument("--run-id")

    serve = subparsers.add_parser("serve", help="start the optional FastAPI service")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8042)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    computer = BioComputer(workspace_root=args.workspace)

    if args.command == "tools":
        print(json.dumps(computer.registry.list(), indent=2))
        return 0

    if args.command == "run":
        receipt = computer.execute(
            task=args.task,
            tool=args.tool,
            payload=_load_payload(args.payload),
            run_id=args.run_id,
        )
        print(json.dumps(receipt, indent=2))
        return 0 if receipt["status"] == "completed" else 2

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError as exc:
            raise SystemExit("Install the API extra: pip install -e '.[api]'") from exc
        uvicorn.run("raven_biocomputer.api:app", host=args.host, port=args.port, reload=False)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
