from __future__ import annotations

import logging
import os

import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

load_dotenv()


class GeminiLLMClient:
    """Google Gemini LLM client.

    Public interface intentionally matches the previous GitHubLLMClient
    so the rest of the Sentinel architecture remains unchanged.
    """

    def __init__(self) -> None:
        logger.info("Initializing Gemini LLM module")

        self.provider = self._get_env("LLM_PROVIDER")
        self.model = self._get_env("LLM_MODEL")
        self.api_key = self._get_env("GOOGLE_API_KEY")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

        self._llm = self._initialize_llm()

        logger.info("Gemini LLM configuration loaded successfully.")

    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Create the Gemini chat model."""
        if self.provider.lower() != "gemini":
            raise ValueError(f"Unsupported provider: {self.provider}")

        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=self.temperature,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response from Google Gemini.

        Parameters
        ----------
        system_prompt
            Instructions defining the LLM's role.
        user_prompt
            User input.

        Returns
        -------
        str
            Generated response.
        """
        if not system_prompt or not system_prompt.strip():
            raise ValueError("system_prompt must be a non‑empty string")
        # Allow empty user_prompt; treat as empty string
        if user_prompt is None:
            user_prompt = ""
        # Ensure user_prompt is a string
        if not isinstance(user_prompt, str):
            raise ValueError("user_prompt must be a string")

        messages = [
            SystemMessage(content=system_prompt),
        ]
        if user_prompt.strip():
            messages.append(HumanMessage(content=user_prompt))

        # If user_prompt is empty after stripping, return a placeholder without invoking LLM
        if not user_prompt.strip():
            raise ValueError("user_prompt cannot be empty after stripping whitespace.")
        _MAX_ATTEMPTS = 2
        _RETRY_WAIT_SECONDS = 2

        last_exc: Exception | None = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = self._llm.invoke(messages)
                break
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "rate" in err_str:
                    if attempt < _MAX_ATTEMPTS:
                        logger.warning(
                            "Gemini rate limit hit on attempt %d. "
                            "Retrying in %ds.",
                            attempt,
                            _RETRY_WAIT_SECONDS,
                        )
                        time.sleep(_RETRY_WAIT_SECONDS)
                        continue
                    raise RuntimeError(
                        "LLM rate limit reached. Please try again in a moment."
                    ) from e
                raise RuntimeError("LLM invocation failed.") from e
        else:
            raise RuntimeError("LLM invocation failed after retries.") from last_exc


        content = response.content

        # Gemini may return a list of blocks or a single string.
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text")
                elif hasattr(block, "text"):
                    text = block.text
                else:
                    text = str(block)
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts).strip()

        return str(content).strip()

    @staticmethod
    def _get_env(name: str) -> str:
        """Read and validate an environment variable."""
        value = os.getenv(name)
        if value is None or not value.strip():
            raise ValueError(f"Required environment variable '{name}' is missing.")
        return value.strip()