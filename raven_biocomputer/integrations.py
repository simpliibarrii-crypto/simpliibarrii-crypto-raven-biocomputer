from __future__ import annotations

from typing import Any

from .models import RunReceipt


def build_integrations(receipt: RunReceipt) -> dict[str, Any]:
    claim_id = f"claim:{receipt.run_id}:result"
    source_id = f"source:{receipt.run_id}:tool"
    approved = bool(receipt.policy and receipt.policy.allowed and receipt.status == "completed")

    return {
        "raven_evidence_graph": {
            "schema": "raven.evidence_graph.v1",
            "sources": [{"id": source_id, "kind": "bounded-tool-run", "title": f"{receipt.tool} execution", "digest": receipt.input_digest}],
            "claims": [{"id": claim_id, "text": f"The {receipt.tool} tool produced the attached structured result.", "source_ids": [source_id], "confidence": 1.0 if approved else 0.0, "risk": receipt.policy.level if receipt.policy else "unknown"}],
            "answer_trace": {"question": receipt.task, "claim_ids": [claim_id]},
        },
        "jspace_envelope": {
            "schema": "jspace.chain.envelope.v1",
            "workspace": "raven-biocomputer",
            "run_id": receipt.run_id,
            "policy_gate": receipt.policy.to_dict() if receipt.policy else None,
            "structured_reflection": {"status": receipt.status, "tool": receipt.tool, "artifact_count": len(receipt.artifacts)},
        },
        "home_for_ai": {
            "schema": "home.raven_run_record.v1",
            "run_id": receipt.run_id,
            "surface": "raven-biocomputer",
            "replayable": approved,
            "input_digest": receipt.input_digest,
            "privacy": "local",
        },
        "hermes_edge": {
            "schema": "hermes.edge.task.v1",
            "preferred_route": "deterministic-tool-first",
            "tool": receipt.tool,
            "cloud_required": False,
        },
        "openclinical_ai": {
            "schema": "openclinical.biocomputer.bridge.v1",
            "clinical_use": False,
            "human_review_required": bool(receipt.policy and receipt.policy.requires_human_review),
        },
    }
