from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

_RUN_ID_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_run_id(value: str) -> str:
    cleaned = _RUN_ID_RE.sub("-", value.strip()).strip("-.")
    if not cleaned:
        raise ValueError("run_id must contain at least one safe character")
    return cleaned[:96]


def resolve_inside(root: Path, relative: str | Path) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError("path escapes the BioComputer workspace")
    return candidate
