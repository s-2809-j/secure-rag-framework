from src.llm.gemini_client import GeminiLLMClient


def main():
    print("Initializing Gemini LLM client...")

    client = GeminiLLMClient()

    print("Client initialized successfully.")

    prompt = "Reply with exactly one word: SUCCESS"

    print("Sending test request...")

    response = client.invoke(prompt)

    print("\nModel Response:")
    print(response)


if __name__ == "__main__":
    main()