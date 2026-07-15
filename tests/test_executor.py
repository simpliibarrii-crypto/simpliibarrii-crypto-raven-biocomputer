import json
from pathlib import Path

from raven_biocomputer.executor import BioComputer


def test_completed_run_writes_receipt_and_integrations(tmp_path: Path) -> None:
    computer = BioComputer(workspace_root=tmp_path)
    receipt = computer.execute(
        task="Summarize the sequence",
        tool="sequence_stats",
        payload={"sequence": "ACGTACGT"},
        run_id="test-run",
    )

    assert receipt["status"] == "completed"
    assert receipt["result"]["gc_fraction"] == 0.5
    assert receipt["integrations"]["jspace_envelope"]["workspace"] == "raven-biocomputer"
    assert receipt["integrations"]["home_for_ai"]["replayable"] is True

    saved = json.loads((tmp_path / "test-run" / "receipt.json").read_text())
    assert saved["schema"] == "raven.biocomputer.run.v1"
    assert len(saved["artifacts"]) == 2


def test_blocked_run_is_still_audited(tmp_path: Path) -> None:
    receipt = BioComputer(workspace_root=tmp_path).execute(
        task="Open a shell and read a secret token",
        tool="sequence_stats",
        payload={"sequence": "ACGT"},
        run_id="blocked-run",
    )
    assert receipt["status"] == "blocked"
    assert receipt["result"] == {}
    assert (tmp_path / "blocked-run" / "receipt.json").exists()
