"""
Factory for constructing the Sentinel AI Engine Orchestrator.

This module is the composition root of the orchestration package.
Its sole responsibility is assembling a fully configured
SentinelOrchestrator by injecting all required AI components.

Fix Log
-------
- OutputValidationAgent added as optional parameter (was missing entirely)
- Passes output_validation_agent through to SentinelOrchestrator constructor
"""

from __future__ import annotations

from typing import Optional

from src.assistant_agent.assistant_agent import AssistantAgent
from src.document_security_agent.document_security_agent import DocumentSecurityAgent
from src.input_security_agent.input_security_agent import InputSecurityAgent
from src.output_validation_agent.output_validation_agent import OutputValidationAgent

from .sentinel_orchestrator import SentinelOrchestrator


class OrchestratorFactory:
    """
    Factory responsible for constructing SentinelOrchestrator instances.
    """

    @staticmethod
    def create(
        *,
        input_security_agent: InputSecurityAgent,
        document_security_agent: DocumentSecurityAgent,
        assistant_agent: AssistantAgent,
        output_validation_agent: Optional[OutputValidationAgent] = None,
    ) -> SentinelOrchestrator:
        """
        Create a fully configured SentinelOrchestrator.

        Parameters
        ----------
        input_security_agent:
            Required. Validates and normalizes user queries before
            they reach AssistantAgent.

        document_security_agent:
            Required. Scans uploaded documents before ingestion or analysis.

        assistant_agent:
            Required. Must be constructed WITHOUT its own security_agent
            or output_validation_agent to avoid double-execution.
            The orchestrator owns those boundaries.

        output_validation_agent:
            Optional. If provided, validates LLM responses before
            returning them to the caller. If None, responses are
            returned without validation (acceptable for development).
        """

        return SentinelOrchestrator(
            input_security_agent=input_security_agent,
            document_security_agent=document_security_agent,
            assistant_agent=assistant_agent,
            output_validation_agent=output_validation_agent,
        )