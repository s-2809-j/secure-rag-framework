from __future__ import annotations
import re
import json
import logging
from typing import Any

from src.llm.gemini_client import GeminiLLMClient

from .support.models import Tier2Decision
from ..exceptions import (
    InvalidTier2ResponseError,
    LLMInvocationError,
    Tier2JudgeError,
)

logger = logging.getLogger(__name__)


class Tier2Judge:
    """
    Tier-2 hallucination verifier.

    This component performs a secondary verification using an LLM
    whenever Tier-1 heuristics are unable to confidently determine
    whether a generated sentence is supported by the retrieved
    evidence.

    The judge MUST NOT use external knowledge.

    It evaluates only against the supplied evidence chunks.

    Expected workflow
    -----------------
    1. Build a constrained verification prompt.
    2. Invoke the configured LLM.
    3. Parse the structured JSON response.
    4. Validate the response.
    5. Return a validated Tier2Decision.
    """

    def __init__(
        self,
        llm: GeminiLLMClient,
    ) -> None:
        """
        Initialize the Tier-2 Judge.

        Parameters
        ----------
        llm:
            Production GeminiLLMClient.
        """

        if llm is None:
            raise ValueError("llm cannot be None.")

        self._llm = llm

    ####################################################################
    # Public API
    ####################################################################

    def evaluate(
        self,
        sentence: str,
        evidence_chunks: list[str],
        conversation_context: str |None = None,
    ) -> Tier2Decision:
        """
        Verify whether a sentence is supported by retrieved evidence.

        Parameters
        ----------
        sentence:
            Sentence requiring verification.

        evidence_chunks:
            Retrieved supporting chunks.

        conversation_context:
            Optional previous conversation.

        Returns
        -------
        Tier2Decision

        Raises
        ------
        Tier2JudgeError
        """

        logger.info("Starting Tier-2 verification.")

        sentence = self._validate_sentence(sentence)

        evidence_chunks = self._validate_chunks(
            evidence_chunks
        )

        system_prompt, user_prompt = self._build_prompt(
            sentence=sentence,
            evidence_chunks=evidence_chunks,
            conversation_context=conversation_context,
        )

        raw_response = self._invoke_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        logger.debug("Raw Tier-2 response:\n%s", raw_response)

        parsed = self._parse_response(raw_response)

        decision = self._validate_response(
            parsed,
            len(evidence_chunks),
        )   

        logger.info(
            "Tier-2 verification completed. "
            "Supported=%s Confidence=%.3f",
            decision.supported,
            decision.confidence,
        )

        return decision

    ####################################################################
    # Validation Helpers
    ####################################################################

    @staticmethod
    def _validate_sentence(
        sentence: str,
    ) -> str:
        """
        Validate sentence input.
        """

        if not isinstance(sentence, str):
            raise Tier2JudgeError(
                "Sentence must be a string."
            )

        sentence = sentence.strip()

        if not sentence:
            raise Tier2JudgeError(
                "Sentence cannot be empty."
            )

        return sentence

    @staticmethod
    def _validate_chunks(
        chunks: list[str],
    ) -> list[str]:
        """
        Validate retrieved evidence.
        """

        if not isinstance(chunks, list):
            raise Tier2JudgeError(
                "Evidence must be a list."
            )

        cleaned: list[str] = []

        for chunk in chunks:

            if not isinstance(chunk, str):
                continue

            chunk = chunk.strip()

            if chunk:
                cleaned.append(chunk)

        if not cleaned:
            raise Tier2JudgeError(
                "No valid evidence chunks supplied."
            )

        return cleaned
        ####################################################################
    # Prompt Construction
    ####################################################################

    def _build_prompt(
        self,
        sentence: str,
        evidence_chunks: list[str],
        conversation_context: str | None,
    ) -> tuple[str, str]:
        """
        Build the system and user prompts.

        The Tier-2 Judge must evaluate the sentence strictly
        against the supplied evidence. External knowledge,
        assumptions, or world facts are prohibited.
        """

        system_prompt = """
        You are the Tier-2 Verification Judge of the Sentinel Secure RAG System.

        Your responsibility is to determine whether ONE generated sentence is
        supported ONLY by the supplied evidence.

        Rules:

        1. Never use external knowledge.

        2. Ignore everything not present inside the evidence.

        3. If evidence partially supports the statement,
        classify it as unsupported.

        4. If numbers differ,
        classify as unsupported.

        5. Never infer missing information.

        6. Base every decision only on the supplied evidence.

        7. Return ONLY valid JSON.

        Output Schema:

        {
            "supported": true,
            "confidence": 0.97,
            "reason": "...",
            "evidence_indices": [0]
        }
        """.strip()

        evidence_text = self._format_evidence(
            evidence_chunks
        )

        context_section = ""

        if conversation_context:

            context = conversation_context.strip()

            if context:

                context_section = (
                    "Conversation Context\n"
                    "--------------------\n"
                    f"{context}\n\n"
                )

        user_prompt = (
            "Evaluate the following sentence.\n\n"
            f"{context_section}"
            "Sentence\n"
            "--------\n"
            f"{sentence}\n\n"
            "Evidence\n"
            "--------\n"
            f"{evidence_text}\n\n"
            "Return only JSON."
        )

        return system_prompt, user_prompt

    ####################################################################
    # Prompt Helpers
    ####################################################################

    @staticmethod
    def _format_evidence(
        evidence_chunks: list[str],
    ) -> str:
        """
        Format retrieved evidence into a deterministic prompt.

        Each chunk receives a stable numeric identifier so the
        LLM can reference supporting evidence using indices.
        """

        sections: list[str] = []

        for index, chunk in enumerate(evidence_chunks):

            sections.append(
                f"[Chunk {index}]\n"
                f"{chunk}"
            )

        return "\n\n".join(sections)

        ####################################################################
    # LLM Invocation
    ####################################################################

    def _invoke_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Invoke the configured GitHub LLM.

        Raises
        ------
        LLMInvocationError
            If the model invocation fails.
        """

        logger.debug("Invoking Tier-2 LLM.")

        try:

            response = self._llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        except Exception as exc:
            logger.exception(
                "Tier-2 LLM invocation failed."
            )
            raise LLMInvocationError(
                "Failed to invoke Tier-2 LLM."
            ) from exc

        if not isinstance(response, str):
            raise LLMInvocationError(
                "LLM returned a non-string response."
            )

        response = response.strip()

        if not response:
            raise LLMInvocationError(
                "LLM returned an empty response."
            )

        logger.debug(
            "Received Tier-2 response (%d characters).",
            len(response),
        )

        return response

    ####################################################################
    # Response Parsing
    ####################################################################

    def _parse_response(self, response: str):
        response = response.strip()

        # Remove Markdown fences.
        response = re.sub(
            r"^```(?:json)?\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )
        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        # Extract JSON object.
        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL,
        )

        if match:
            response = match.group(0)

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            raise InvalidTier2ResponseError(
                "Tier-2 returned invalid JSON."
            ) from exc
    ####################################################################
    # Response Validation
    ####################################################################

    def _validate_response(
        self,
        response: dict[str, Any],
        chunk_count: int,
    ) -> Tier2Decision:
        """
        Validate the parsed response and convert it into a
        Tier2Decision.
        """

        required_fields = (
            "supported",
            "confidence",
            "reason",
            "evidence_indices",
        )

        missing = [
            field
            for field in required_fields
            if field not in response
        ]

        if missing:

            raise InvalidTier2ResponseError(
                "Missing required fields: "
                + ", ".join(missing)
            )

        supported = response["supported"]
        confidence = response["confidence"]
        reason = response["reason"]
        evidence_indices = response["evidence_indices"]

        if not isinstance(supported, bool):

            raise InvalidTier2ResponseError(
                "'supported' must be boolean."
            )

        if not isinstance(confidence, (int, float)):

            raise InvalidTier2ResponseError(
                "'confidence' must be numeric."
            )

        confidence = float(confidence)

        if confidence < 0.0 or confidence > 1.0:

            raise InvalidTier2ResponseError(
                "'confidence' must lie between 0 and 1."
            )

        if not isinstance(reason, str):

            raise InvalidTier2ResponseError(
                "'reason' must be a string."
            )

        reason = reason.strip()

        if not reason:

            raise InvalidTier2ResponseError(
                "'reason' cannot be empty."
            )

        if not isinstance(evidence_indices, list):

            raise InvalidTier2ResponseError(
                "'evidence_indices' must be a list."
            )

        validated_indices: list[int] = []

        for index in evidence_indices:

            if not isinstance(index, int):

                raise InvalidTier2ResponseError(
                    "Evidence indices must be integers."
                )

            if index < 0 or index >= chunk_count:

                raise InvalidTier2ResponseError(
                    f"Evidence index {index} is out of range."
                )

            if index not in validated_indices:
                validated_indices.append(index)

        decision = Tier2Decision(
            supported=supported,
            confidence=confidence,
            reason=reason,
            evidence_indices=validated_indices,
        )

        logger.debug(
            "Tier-2 decision validated successfully."
        )

        return decision