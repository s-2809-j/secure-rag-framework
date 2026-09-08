from __future__ import annotations

from src.assistant_agent.assistant_agent import AssistantAgent


# ---------------------------------------------------------------------
# Fake Objects
# ---------------------------------------------------------------------

class FakeRetriever:
    """Dummy retriever for AssistantAgent initialization."""
    pass


class FakeLLM:
    """Dummy LLM for AssistantAgent initialization."""
    pass


class FakeDecision:
    """Represents a successful document security decision."""

    def __init__(self) -> None:
        self.allowed = True


class FakeDocumentSecurityAgent:
    """Fake DocumentSecurityAgent."""

    def analyze(self, file_path: str, metadata: dict):
        print("DocumentSecurityAgent.analyze() called")
        print(f"File: {file_path}")

        return FakeDecision()


# ---------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------

def main() -> None:

    assistant = AssistantAgent(
        retriever=FakeRetriever(),
        llm=FakeLLM(),
        document_security_agent=FakeDocumentSecurityAgent(),
    )

    decision = assistant.analyze_document(
        file_path="sample.md",
        metadata={},
    )

    print()

    print("===== TEST RESULT =====")

    print("Decision Allowed :", decision.allowed)

    assert decision.allowed is True

    print("TEST PASSED")


if __name__ == "__main__":
    main()