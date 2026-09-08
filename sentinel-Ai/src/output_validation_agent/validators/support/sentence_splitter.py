from __future__ import annotations

import re


class SentenceSplitter:
    """
    Splits an LLM response into individual sentences (claims).

    The splitter performs lightweight normalization and returns
    a list of non-empty sentences while preserving their order.

    This component is intentionally deterministic and does not
    perform any semantic analysis.
    """

    _SENTENCE_PATTERN = re.compile(
        r"(?<=[.!?])\s+"
    )

    def split(
        self,
        text: str,
    ) -> list[str]:
        """
        Split the supplied text into sentences.

        Args:
            text:
                The LLM-generated response.

        Returns:
            List of cleaned sentences.
        """

        if not isinstance(text, str):
            raise TypeError(
                "Expected text to be of type 'str'."
            )

        text = text.strip()

        if not text:
            return []

        sentences = self._SENTENCE_PATTERN.split(text)

        cleaned_sentences: list[str] = []

        for sentence in sentences:

            sentence = self._normalize(sentence)

            if sentence:
                cleaned_sentences.append(sentence)

        return cleaned_sentences

    @staticmethod
    def _normalize(
        sentence: str,
    ) -> str:
        """
        Normalize whitespace within a sentence.
        """

        return " ".join(sentence.split())