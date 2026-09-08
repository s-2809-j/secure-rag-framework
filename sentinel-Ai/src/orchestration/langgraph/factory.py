"""
Factory for constructing the compiled Sentinel LangGraph.

This is the composition root for the LangGraph layer.
Its sole responsibility is assembling a compiled graph by injecting
all required agent dependencies.

This factory is intentionally parallel to OrchestratorFactory.
Both factories accept the same agent parameters and produce objects
with the same logical contract (execute a Sentinel workflow).

The SentinelOrchestrator and the LangGraph graph are independent.
Neither depends on the other. The application entry point chooses
which one to invoke.
"""

from __future__ import annotations

import logging
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver

from src.assistant_agent.assistant_agent import AssistantAgent
from src.input_security_agent.input_security_agent import InputSecurityAgent
from src.output_validation_agent.output_validation_agent import OutputValidationAgent

from .graph import build_sentinel_graph

logger = logging.getLogger(__name__)


class LangGraphOrchestratorFactory:
    """
    Factory responsible for constructing the compiled Sentinel LangGraph.

    Mirrors OrchestratorFactory in parameter contract so both can be
    driven from the same composition root in tests and application code.
    """

    @staticmethod
    def create(
        *,
        input_security_agent: InputSecurityAgent,
        assistant_agent: AssistantAgent,
        output_validation_agent: Optional[OutputValidationAgent] = None,
        checkpointer: Optional[MemorySaver] = None,
    ):
        """
        Construct and return a compiled Sentinel LangGraph.

        Parameters
        ----------
        input_security_agent:
            Required. Validates and normalizes user queries.

        assistant_agent:
            Required. Must be constructed WITHOUT its own security_agent
            or output_validation_agent. The graph owns those boundaries.

        output_validation_agent:
            Optional. If None, LLM responses are returned without
            output validation (acceptable for development/testing).

        checkpointer:
            Optional. Defaults to MemorySaver. Override for custom
            persistence (e.g. SqliteSaver for cross-process state).

        Returns
        -------
        CompiledGraph
            Ready for graph.invoke(initial_state, config).
        """

        logger.info("LangGraphOrchestratorFactory: creating compiled graph.")

        compiled_graph = build_sentinel_graph(
            input_security_agent=input_security_agent,
            assistant_agent=assistant_agent,
            output_validation_agent=output_validation_agent,
            checkpointer=checkpointer,
        )

        logger.info(
            "LangGraphOrchestratorFactory: compiled graph created successfully."
        )

        return compiled_graph