from pathlib import Path

import pytest

from raven_biocomputer.security import resolve_inside, safe_run_id


def test_safe_run_id_normalizes_spaces() -> None:
    assert safe_run_id("run alpha") == "run-alpha"


def test_workspace_escape_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="escapes"):
        resolve_inside(tmp_path, "../outside")
