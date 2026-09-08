from __future__ import annotations

import logging
import re

from src.output_validation_agent.validators.support.models import (
    HeuristicResult,
)

logger = logging.getLogger(__name__)


class _BaseLexicalScorer:
    """
    Shared validation utilities for lexical scorers.
    """

    @staticmethod
    def _validate_input(
        sentence: str,
        candidates: list[str],
    ) -> list[str]:

        if not isinstance(sentence, str):
            raise TypeError(
                "Expected sentence to be of type 'str'."
            )

        sentence = sentence.strip()

        if not sentence:
            raise ValueError(
                "Sentence cannot be empty."
            )

        valid_candidates: list[str] = []

        for candidate in candidates:

            if not isinstance(candidate, str):
                raise TypeError(
                    "Expected candidate to be of type 'str'."
                )

            candidate = candidate.strip()

            if candidate:
                valid_candidates.append(candidate)

        return valid_candidates


class KeywordOverlapScorer(_BaseLexicalScorer):
    """
    Computes keyword overlap using Jaccard similarity.
    """

    _WORD_PATTERN = re.compile(
        r"\b[a-zA-Z][a-zA-Z0-9_-]*\b"
    )

    _STOP_WORDS = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "by",
        "with",
        "from",
        "that",
        "this",
        "it",
        "as",
        "at",
    }

    def score(
        self,
        sentence: str,
        candidates: list[str],
    ) -> HeuristicResult:

        candidates = self._validate_input(
            sentence,
            candidates,
        )

        sentence_keywords = self._extract_keywords(
            sentence
        )

        if not sentence_keywords:
            return HeuristicResult(
                name="keyword_overlap",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "sentence_keywords": [],
                    "matched_keywords": [],
                },
            )

        candidate_keywords: set[str] = set()

        for candidate in candidates:
            candidate_keywords.update(
                self._extract_keywords(candidate)
            )

        if not candidate_keywords:
            return HeuristicResult(
                name="keyword_overlap",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "sentence_keywords": sorted(
                        sentence_keywords
                    ),
                    "matched_keywords": [],
                },
            )

        intersection = (
            sentence_keywords
            & candidate_keywords
        )

        union = (
            sentence_keywords
            | candidate_keywords
        )

        score = (
            len(intersection)
            / len(union)
        )

        logger.debug(
            "Keyword overlap score: %.3f",
            score,
        )

        return HeuristicResult(
            name="keyword_overlap",
            applicable=True,
            score=score,
            confidence=1.0,
            metadata={
                "sentence_keywords": sorted(
                    sentence_keywords
                ),
                "matched_keywords": sorted(
                    intersection
                ),
            },
        )

    def _extract_keywords(
        self,
        text: str,
    ) -> set[str]:

        keywords = {
            token.lower()
            for token in self._WORD_PATTERN.findall(text)
        }

        return {
            token
            for token in keywords
            if token not in self._STOP_WORDS
        }


class EntityOverlapScorer(_BaseLexicalScorer):
    """
    Computes overlap between named entities appearing
    in the sentence and candidate texts.
    """

    _ENTITY_PATTERN = re.compile(
        r"\b[A-Z][A-Za-z0-9_-]*\b"
    )

    def score(
        self,
        sentence: str,
        candidates: list[str],
    ) -> HeuristicResult:

        candidates = self._validate_input(
            sentence,
            candidates,
        )

        sentence_entities = self._extract_entities(
            sentence
        )

        if not sentence_entities:
            return HeuristicResult(
                name="entity_overlap",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "sentence_entities": [],
                    "matched_entities": [],
                },
            )

        candidate_entities: set[str] = set()

        for candidate in candidates:
            candidate_entities.update(
                self._extract_entities(candidate)
            )

        if not candidate_entities:
            return HeuristicResult(
                name="entity_overlap",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "sentence_entities": sorted(
                        sentence_entities
                    ),
                    "matched_entities": [],
                },
            )

        matched_entities = (
            sentence_entities
            & candidate_entities
        )

        score = (
            len(matched_entities)
            / len(sentence_entities)
        )

        logger.debug(
            "Entity overlap score: %.3f",
            score,
        )

        return HeuristicResult(
            name="entity_overlap",
            applicable=True,
            score=score,
            confidence=1.0,
            metadata={
                "sentence_entities": sorted(
                    sentence_entities
                ),
                "matched_entities": sorted(
                    matched_entities
                ),
            },
        )

    def _extract_entities(
        self,
        text: str,
    ) -> set[str]:

        return {
            match.group(0)
            for match in self._ENTITY_PATTERN.finditer(
                text
            )
        }

class NumericConsistencyScorer(_BaseLexicalScorer):
    """
    Verifies numeric consistency between the sentence
    and the candidate texts.
    """

    _NUMBER_PATTERN = re.compile(
        r"\d+(?:\.\d+)?%?"
    )

    def score(
        self,
        sentence: str,
        candidates: list[str],
    ) -> HeuristicResult:

        candidates = self._validate_input(
            sentence,
            candidates,
        )

        sentence_numbers = set(
            self._NUMBER_PATTERN.findall(sentence)
        )

        if not sentence_numbers:
            return HeuristicResult(
                name="numeric_consistency",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "sentence_numbers": [],
                    "candidate_numbers": [],
                },
            )

        candidate_numbers: set[str] = set()

        for candidate in candidates:
            candidate_numbers.update(
                self._NUMBER_PATTERN.findall(
                    candidate
                )
            )

        matched = (
            sentence_numbers
            <= candidate_numbers
        )

        return HeuristicResult(
            name="numeric_consistency",
            applicable=True,
            score=1.0 if matched else 0.0,
            confidence=1.0,
            metadata={
                "sentence_numbers": sorted(
                    sentence_numbers
                ),
                "candidate_numbers": sorted(
                    candidate_numbers
                ),
                "matched": matched,
            },
        )


class CitationMatchScorer(_BaseLexicalScorer):
    """
    Detects explicit citations appearing in the
    generated sentence.
    """

    _PATTERNS = (
        re.compile(r"Section\s+\d+", re.IGNORECASE),
        re.compile(r"Figure\s+\d+", re.IGNORECASE),
        re.compile(r"Table\s+\d+", re.IGNORECASE),
        re.compile(r"ISO\s+\d+", re.IGNORECASE),
        re.compile(r"RFC\s+\d+", re.IGNORECASE),
        re.compile(r"\[\d+\]"),
    )

    def score(
        self,
        sentence: str,
        candidates: list[str],
    ) -> HeuristicResult:

        candidates = self._validate_input(
            sentence,
            candidates,
        )

        sentence_citations = self._extract(
            sentence
        )

        if not sentence_citations:
            return HeuristicResult(
                name="citation_match",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "citations": [],
                    "matched": [],
                },
            )

        candidate_citations: set[str] = set()

        for candidate in candidates:
            candidate_citations.update(
                self._extract(candidate)
            )

        matched = (
            sentence_citations
            & candidate_citations
        )

        score = (
            len(matched)
            / len(sentence_citations)
        )

        return HeuristicResult(
            name="citation_match",
            applicable=True,
            score=score,
            confidence=1.0,
            metadata={
                "citations": sorted(
                    sentence_citations
                ),
                "matched": sorted(
                    matched
                ),
            },
        )

    def _extract(
        self,
        text: str,
    ) -> set[str]:

        citations: set[str] = set()

        for pattern in self._PATTERNS:
            citations.update(
                pattern.findall(text)
            )

        return citations