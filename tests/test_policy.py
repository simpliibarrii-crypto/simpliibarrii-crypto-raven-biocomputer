from raven_biocomputer.policy import BiologyPolicy


def test_dry_lab_sequence_analysis_is_allowed() -> None:
    decision = BiologyPolicy().evaluate(
        "Calculate GC content", "sequence_stats", {"sequence": "ACGT"}
    )
    assert decision.allowed is True
    assert decision.level == "dry-lab"


def test_clinical_decision_requires_human_review() -> None:
    decision = BiologyPolicy().evaluate(
        "Diagnose this patient-specific condition", "sequence_stats", {"sequence": "ACGT"}
    )
    assert decision.allowed is False
    assert decision.requires_human_review is True
    assert "clinical-decision" in decision.matched_rules


def test_shell_access_is_blocked() -> None:
    decision = BiologyPolicy().evaluate("Open a terminal and run sudo", "shell", {})
    assert decision.allowed is False
    assert decision.level == "blocked"
