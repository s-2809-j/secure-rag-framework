"""
Sentinel LangGraph StateGraph definition.

This module defines the complete workflow graph for the Sentinel AI Engine.
It wires the node factories from nodes.py into a compiled LangGraph
StateGraph with conditional routing that mirrors the SentinelOrchestrator
workflow exactly.

Workflow Branches
-----------------

    START
      │
      ▼
    security_node
      │
      ├─ [blocked=True]                  → blocked_node          → END
      ├─ [workflow=knowledge_upload]     → knowledge_upload_node → END
      ├─ [workflow=document_analysis]    → document_analysis_node→ END
      └─ [workflow=chat]                 → chat_generation_node
                                               │
                                               ├─ [blocked=True] → blocked_node → END
                                               └─ [blocked=False]→ validation_node → END

Routing
-------
_route_after_security: pure function, reads blocked + workflow.
_route_after_generation: pure function, reads blocked after
    chat_generation_node. Routes to blocked_node when generation
    failed (Gemini error, rate limit, etc.) to prevent validation_node
    from receiving an empty raw_response.

Graph Construction
------------------
This module exposes a single public function:

    build_sentinel_graph(
        input_security_agent,
        assistant_agent,
        output_validation_agent,
        checkpointer,
    ) -> CompiledGraph

Called exclusively by LangGraphOrchestratorFactory (factory.py).
Never called directly from application code.
"""

from __future__ import annotations

import logging
from typing import Optional

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.assistant_agent.assistant_agent import AssistantAgent
from src.input_security_agent.input_security_agent import InputSecurityAgent
from src.output_validation_agent.output_validation_agent import OutputValidationAgent

from .nodes import (
    blocked_node,
    make_chat_generation_node,
    make_document_analysis_node,
    make_knowledge_upload_node,
    make_security_node,
    make_validation_node,
)
from .state import SentinelState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Node name constants
# Defined here to eliminate magic strings across the module.
# ---------------------------------------------------------------------------

_NODE_SECURITY = "security_node"
_NODE_CHAT_GENERATION = "chat_generation_node"
_NODE_VALIDATION = "validation_node"
_NODE_DOCUMENT_ANALYSIS = "document_analysis_node"
_NODE_KNOWLEDGE_UPLOAD = "knowledge_upload_node"
_NODE_BLOCKED = "blocked_node"

# WorkflowType string values (StrEnum — matches models.py exactly)
_WORKFLOW_CHAT = "chat"
_WORKFLOW_DOCUMENT_ANALYSIS = "document_analysis"
_WORKFLOW_KNOWLEDGE_UPLOAD = "knowledge_upload"


# ---------------------------------------------------------------------------
# Conditional edge function: after security_node
# ---------------------------------------------------------------------------

def _route_after_security(state: SentinelState) -> str:
    """
    Determine the next node after security_node completes.

    Pure routing function — reads state, returns a node name string.
    No I/O, no agent calls, no side effects.

    Returns
    -------
    str
        One of the node name constants defined in this module.
    """

    if state.get("blocked"):
        logger.debug(
            "_route_after_security: routing to blocked_node. "
            "request_id=%s",
            state.get("request_id"),
        )
        return _NODE_BLOCKED

    workflow = state.get("workflow", "")

    if workflow == _WORKFLOW_KNOWLEDGE_UPLOAD:
        logger.debug(
            "_route_after_security: routing to knowledge_upload_node. "
            "request_id=%s",
            state.get("request_id"),
        )
        return _NODE_KNOWLEDGE_UPLOAD

    if workflow == _WORKFLOW_DOCUMENT_ANALYSIS:
        logger.debug(
            "_route_after_security: routing to document_analysis_node. "
            "request_id=%s",
            state.get("request_id"),
        )
        return _NODE_DOCUMENT_ANALYSIS

    logger.debug(
        "_route_after_security: routing to chat_generation_node. "
        "request_id=%s",
        state.get("request_id"),
    )
    return _NODE_CHAT_GENERATION


# ---------------------------------------------------------------------------
# Conditional edge function: after chat_generation_node
# ---------------------------------------------------------------------------

def _route_after_generation(state: SentinelState) -> str:
    """
    Determine the next node after chat_generation_node completes.

    If chat_generation_node set blocked=True (generation failed — e.g.
    Gemini rate limit, network error, or any unhandled exception),
    route to blocked_node to terminate cleanly.

    If generation succeeded, route to validation_node.

    This guard prevents validation_node from receiving an empty
    raw_response, which causes HallucinationValidator to raise
    ValidatorExecutionError: LLM response cannot be empty.

    Pure routing function — reads state, returns a node name string.
    No I/O, no agent calls, no side effects.

    Returns
    -------
    str
        One of the node name constants defined in this module.
    """

    if state.get("blocked"):
        logger.debug(
            "_route_after_generation: generation failed — routing to blocked_node. "
            "request_id=%s",
            state.get("request_id"),
        )
        return _NODE_BLOCKED

    logger.debug(
        "_route_after_generation: generation succeeded — routing to validation_node. "
        "request_id=%s",
        state.get("request_id"),
    )
    return _NODE_VALIDATION


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_sentinel_graph(
    *,
    input_security_agent: InputSecurityAgent,
    assistant_agent: AssistantAgent,
    output_validation_agent: Optional[OutputValidationAgent] = None,
    checkpointer: Optional[MemorySaver] = None,
):
    """
    Construct and compile the Sentinel LangGraph StateGraph.

    Parameters
    ----------
    input_security_agent:
        Required. Injected into security_node.

    assistant_agent:
        Required. Must be constructed WITHOUT its own security_agent
        or output_validation_agent. Injected into chat_generation_node,
        document_analysis_node, and knowledge_upload_node.

    output_validation_agent:
        Optional. If None, validation_node passes raw_response through
        as final_response without invoking the agent.

    checkpointer:
        Optional. Defaults to MemorySaver (in-memory, stateless per
        process restart). Pass an explicit checkpointer for custom
        persistence behaviour.

    Returns
    -------
    CompiledGraph
        A compiled LangGraph StateGraph ready for graph.invoke().
    """

    logger.info("Building Sentinel LangGraph StateGraph.")

    # ------------------------------------------------------------------
    # Build node callables via factories (dependency injection)
    # ------------------------------------------------------------------

    security_node = make_security_node(input_security_agent)
    chat_generation_node = make_chat_generation_node(assistant_agent)
    validation_node = make_validation_node(output_validation_agent)
    document_analysis_node = make_document_analysis_node(assistant_agent)
    knowledge_upload_node = make_knowledge_upload_node(assistant_agent)

    # ------------------------------------------------------------------
    # Construct StateGraph
    # ------------------------------------------------------------------

    graph = StateGraph(SentinelState)

    # ------------------------------------------------------------------
    # Register nodes
    # ------------------------------------------------------------------

    graph.add_node(_NODE_SECURITY, security_node)
    graph.add_node(_NODE_CHAT_GENERATION, chat_generation_node)
    graph.add_node(_NODE_VALIDATION, validation_node)
    graph.add_node(_NODE_DOCUMENT_ANALYSIS, document_analysis_node)
    graph.add_node(_NODE_KNOWLEDGE_UPLOAD, knowledge_upload_node)
    graph.add_node(_NODE_BLOCKED, blocked_node)

    # ------------------------------------------------------------------
    # Entry edge
    # ------------------------------------------------------------------

    graph.add_edge(START, _NODE_SECURITY)

    # ------------------------------------------------------------------
    # Conditional routing after security_node
    # ------------------------------------------------------------------

    graph.add_conditional_edges(
        _NODE_SECURITY,
        _route_after_security,
        {
            _NODE_BLOCKED: _NODE_BLOCKED,
            _NODE_CHAT_GENERATION: _NODE_CHAT_GENERATION,
            _NODE_DOCUMENT_ANALYSIS: _NODE_DOCUMENT_ANALYSIS,
            _NODE_KNOWLEDGE_UPLOAD: _NODE_KNOWLEDGE_UPLOAD,
        },
    )

    # ------------------------------------------------------------------
    # Conditional routing after chat_generation_node.
    # Routes to blocked_node when generation failed (blocked=True)
    # instead of passing an empty raw_response into validation_node.
    # ------------------------------------------------------------------

    graph.add_conditional_edges(
        _NODE_CHAT_GENERATION,
        _route_after_generation,
        {
            _NODE_BLOCKED: _NODE_BLOCKED,
            _NODE_VALIDATION: _NODE_VALIDATION,
        },
    )

    # ------------------------------------------------------------------
    # Terminal edges
    # ------------------------------------------------------------------

    graph.add_edge(_NODE_VALIDATION, END)
    graph.add_edge(_NODE_DOCUMENT_ANALYSIS, END)
    graph.add_edge(_NODE_KNOWLEDGE_UPLOAD, END)
    graph.add_edge(_NODE_BLOCKED, END)

    # ------------------------------------------------------------------
    # Compile
    # ------------------------------------------------------------------

    active_checkpointer = checkpointer if checkpointer is not None else MemorySaver()

    compiled = graph.compile(checkpointer=active_checkpointer)

    logger.info("Sentinel LangGraph StateGraph compiled successfully.")

    return compiled