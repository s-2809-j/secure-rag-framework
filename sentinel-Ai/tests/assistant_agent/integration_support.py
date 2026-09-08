"""
Shared helpers for AssistantAgent integration tests.
"""

from __future__ import annotations

from typing import Any

from src.assistant_agent.assistant_agent import AssistantAgent

from src.input_security_agent.models import (
    AgentDecision,
    SecurityContext,
)

from src.knowledge_base.models import RetrievedChunk

from src.output_validation_agent.models import (
    ValidationContext,
    ValidationDecision,
)


class FakeInputSecurityAgent:

    def __init__(self, decision: AgentDecision) -> None:
        self._decision = decision

    def analyze(
        self,
        context: SecurityContext,
    ) -> AgentDecision:
        return self._decision


class FakeRetriever:

    def __init__(
        self,
        chunks: list[RetrievedChunk],
    ) -> None:
        self._chunks = chunks

    def retrieve(
        self,
        *,
        query: str,
        top_k: int,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievedChunk]:
        return self._chunks


class FakeLLM:

    def __init__(
        self,
        response: str,
    ) -> None:
        self._response = response

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return self._response


class FakeOutputValidationAgent:

    def __init__(
        self,
        decision: ValidationDecision,
    ) -> None:
        self._decision = decision

    def validate(
        self,
        context: ValidationContext,
    ) -> ValidationDecision:
        return self._decision


def build_chunk(
    content: str,
    *,
    source: str = "test.md",
    distance: float = 0.0,
) -> RetrievedChunk:

    return RetrievedChunk(
        content=content,
        metadata={
            "source": source,
        },
        distance=distance,
    )


def build_agent(
    *,
    security_decision: AgentDecision,
    retrieved_chunks: list[RetrievedChunk],
    llm_response: str,
    output_validation_decision: ValidationDecision,
) -> AssistantAgent:

    return AssistantAgent(
        retriever=FakeRetriever(retrieved_chunks),
        llm=FakeLLM(llm_response),
        security_agent=FakeInputSecurityAgent(
            security_decision
        ),
        output_validation_agent=FakeOutputValidationAgent(
            output_validation_decision
        ),
    )