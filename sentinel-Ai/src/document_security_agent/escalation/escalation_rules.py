"""
Configuration for the Document Escalation subsystem.

This module defines the default thresholds and limits used by the
PriorityEvaluator when determining whether a document chunk should
be escalated for Tier-2 analysis.

The values defined here are intentionally isolated from the
evaluation logic to improve maintainability and configurability.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.document_security_agent.models import EscalationPriority


@dataclass(frozen=True, slots=True)
class EscalationRules:
    """
    Immutable configuration for escalation evaluation.

    Attributes:
        high_confidence_threshold:
            Minimum confidence required for HIGH priority escalation.

        medium_confidence_threshold:
            Minimum confidence required for MEDIUM priority escalation.

        minimum_findings:
            Minimum number of Tier-1 findings required before a chunk
            becomes eligible for escalation.

        default_priority:
            Priority assigned when no escalation rule matches.
    """

    high_confidence_threshold: float = 0.90
    medium_confidence_threshold: float = 0.70
    minimum_findings: int = 1

    default_priority: EscalationPriority = EscalationPriority.LOW


DEFAULT_ESCALATION_RULES = EscalationRules()