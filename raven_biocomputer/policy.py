from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import PolicyDecision


class BiologyPolicy:
    """Dependency-free safety gate for the MVP.

    This policy intentionally allows ordinary dry-lab sequence analysis while
    routing sensitive clinical, wet-lab, pathogen, and genome-editing work to a
    human reviewer. It is a guardrail, not a substitute for institutional review.
    """

    BLOCKED_RULES = {
        "arbitrary-shell": ("shell", "terminal", "bash", "powershell", "sudo", "exec command"),
        "credential-access": ("password", "api key", "secret token", "private key", "credential"),
        "network-exfiltration": ("upload private", "exfiltrate", "send patient data", "bypass firewall"),
    }

    REVIEW_RULES = {
        "clinical-decision": (
            "diagnose",
            "prescribe",
            "treatment recommendation",
            "patient-specific",
            "medical decision",
        ),
        "raw-phi": ("patient name", "health card", "medical record number", "raw phi"),
        "wet-lab-execution": (
            "run the instrument",
            "execute protocol",
            "pipetting robot",
            "order reagent",
        ),
        "genome-editing": ("crispr", "gene drive", "genome editing", "edit this organism"),
        "pathogen-engineering": (
            "increase virulence",
            "evade immunity",
            "engineer pathogen",
            "enhance transmissibility",
        ),
    }

    def evaluate(
        self,
        task: str,
        tool: str,
        payload: Mapping[str, Any] | None = None,
    ) -> PolicyDecision:
        payload = payload or {}
        text = f"{task} {tool} {payload}".lower()

        blocked = tuple(
            rule
            for rule, phrases in self.BLOCKED_RULES.items()
            if any(phrase in text for phrase in phrases)
        )
        if blocked:
            return PolicyDecision(
                allowed=False,
                level="blocked",
                reason="The request crosses a host, credential, or data-exfiltration boundary.",
                matched_rules=blocked,
            )

        review = tuple(
            rule
            for rule, phrases in self.REVIEW_RULES.items()
            if any(phrase in text for phrase in phrases)
        )
        if review:
            return PolicyDecision(
                allowed=False,
                level="human-review",
                reason="The request requires qualified human review before execution.",
                requires_human_review=True,
                matched_rules=review,
            )

        return PolicyDecision(
            allowed=True,
            level="dry-lab",
            reason="Approved for bounded, local dry-lab analysis.",
        )
