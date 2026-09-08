from __future__ import annotations

import logging

import numpy as np

from src.knowledge_base.embedder import Embedder
from src.output_validation_agent.validators.support.models import (
    HeuristicResult,
)

logger = logging.getLogger(__name__)


class SemanticSimilarityScorer:
    """
    Computes semantic similarity between a source sentence
    and a collection of candidate texts.

    The scorer is intentionally generic and can be reused
    across different validators.
    """

    def __init__(
        self,
        embedder: Embedder,
    ) -> None:
        self._embedder = embedder

    def score(
        self,
        source: str,
        candidates: list[str],
    ) -> HeuristicResult:
        """
        Compute the highest semantic similarity between
        the source text and the supplied candidates.
        """

        if not isinstance(source, str):
            raise TypeError(
                "Expected source to be of type 'str'."
            )

        if not candidates:
            return HeuristicResult(
                name="semantic_similarity",
                applicable=False,
                score=None,
                confidence=0.0,
                metadata={
                    "best_match": None,
                },
            )

        logger.debug(
            "Computing semantic similarity "
            "against %d candidates.",
            len(candidates),
        )

        source_embedding = self._embedder.embed_text(
            source
        )

        best_score = -1.0
        best_match = None

        for candidate in candidates:

            candidate_embedding = (
                self._embedder.embed_text(candidate)
            )

            similarity = self._cosine_similarity(
                source_embedding,
                candidate_embedding,
            )

            if similarity > best_score:
                best_score = similarity
                best_match = candidate

        logger.debug(
            "Best semantic similarity: %.3f",
            best_score,
        )

        return HeuristicResult(
            name="semantic_similarity",
            applicable=True,
            score=best_score,
            confidence=1.0,
            metadata={
                "best_match": best_match,
            },
        )

    @staticmethod
    def _cosine_similarity(
        vector_a: np.ndarray,
        vector_b: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between two vectors.
        """

        denominator = (
            np.linalg.norm(vector_a)
            * np.linalg.norm(vector_b)
        )

        if denominator == 0:
            return 0.0

        similarity = (
            np.dot(vector_a, vector_b)
            / denominator
        )

        return float(similarity)