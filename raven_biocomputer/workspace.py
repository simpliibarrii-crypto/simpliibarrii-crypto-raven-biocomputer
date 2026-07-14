from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .security import resolve_inside, safe_run_id


class RunWorkspace:
    def __init__(self, root: str | Path = "runs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, run_id: str) -> Path:
        directory = resolve_inside(self.root, safe_run_id(run_id))
        directory.mkdir(parents=False, exist_ok=False)
        return directory

    def write_json(self, run_dir: Path, name: str, value: Any) -> Path:
        target = resolve_inside(run_dir, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return target

    def read_receipt(self, run_id: str) -> dict[str, Any]:
        target = resolve_inside(self.root, Path(safe_run_id(run_id)) / "receipt.json")
        if not target.exists():
            raise FileNotFoundError(run_id)
        return json.loads(target.read_text(encoding="utf-8"))
