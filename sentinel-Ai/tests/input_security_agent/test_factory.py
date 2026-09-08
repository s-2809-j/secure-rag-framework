"""
Integration tests for InputSecurityFactory.

Run:
    python -m tests.input_security_agent.test_factory
"""

from src.input_security_agent.factory.factory import (
    InputSecurityFactory,
)
from src.input_security_agent.input_security_agent import InputSecurityAgent


def test_create_agent() -> None:
    """
    Verify that the factory successfully constructs
    a fully configured InputSecurityAgent.
    """

    print("=" * 70)
    print("Testing InputSecurityFactory")
    print("=" * 70)

    agent = InputSecurityFactory.create_agent()

    assert agent is not None
    assert isinstance(agent, InputSecurityAgent)

    print("[PASS] InputSecurityAgent instance created successfully.")


def main() -> None:
    """
    Execute all factory tests.
    """

    test_create_agent()

    print()
    print("=" * 70)
    print("All InputSecurityFactory tests passed.")
    print("=" * 70)


if __name__ == "__main__":
    main()