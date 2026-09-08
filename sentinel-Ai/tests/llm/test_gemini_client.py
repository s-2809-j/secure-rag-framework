from __future__ import annotations

import traceback

from src.llm.gemini_client import GeminiLLMClient


def test_constructor() -> None:
    print("\n[TEST] Gemini Client Constructor")

    client = GeminiLLMClient()

    assert client is not None

    print("[PASS] Gemini client initialized successfully.")


def test_generate_response() -> None:
    print("\n[TEST] Gemini Response Generation")

    client = GeminiLLMClient()

    system_prompt = (
        "You are a helpful AI assistant."
    )

    user_prompt = (
        "What is a savings account? "
        "Answer in 2-3 sentences."
    )

    response = client.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    print("\n-------------------------------")
    print("TYPE :", type(response))
    print("-------------------------------")
    print(response)
    print("-------------------------------")

    assert response is not None
    assert isinstance(response, str)
    assert response.strip() != ""

    print("[PASS] Gemini generated a valid response.")


def test_empty_prompt() -> None:
    print("\n[TEST] Empty Prompt")

    client = GeminiLLMClient()

    response = client.generate(
        system_prompt="You are a helpful AI.",
        user_prompt="",
    )

    print("\nTYPE :", type(response))
    print(response)

    assert isinstance(response, str)

    print("[PASS] Empty prompt handled successfully.")


def test_long_prompt() -> None:
    print("\n[TEST] Long Prompt")

    client = GeminiLLMClient()

    prompt = "Explain RAG. " * 300

    response = client.generate(
        system_prompt="You are an expert.",
        user_prompt=prompt,
    )

    print("\nTYPE :", type(response))
    print("Length :", len(response))

    assert isinstance(response, str)

    print("[PASS] Long prompt handled successfully.")


def main() -> None:
    print("=" * 70)
    print("Gemini Client Tests")
    print("=" * 70)

    try:
        test_constructor()
        test_generate_response()
        test_empty_prompt()
        test_long_prompt()

    except Exception:
        print("\n[FAILED]")
        traceback.print_exc()
        raise

    print("\n" + "=" * 70)
    print("All Gemini client tests passed.")
    print("=" * 70)


if __name__ == "__main__":
    main()