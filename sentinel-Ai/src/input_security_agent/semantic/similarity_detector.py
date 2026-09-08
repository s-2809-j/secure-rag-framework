from __future__ import annotations

import logging
from src.input_security_agent.models import (SecurityContext, ValidationResult,AttackCategory,DetectionMatch)

from src.knowledge_base.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore
from src.input_security_agent.detectors.base import BaseDetector
logger = logging.getLogger(__name__)


class SimilarityDetector(BaseDetector):

    DEFAULT_SIMILARITY_THRESHOLD = 0.85

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
      

        if embedder is None:
            raise ValueError(
                "embedder cannot be None."
            )

        if vector_store is None:
            raise ValueError(
                "vector_store cannot be None."
            )

        if not (0.0 <= similarity_threshold <= 1.0):
            raise ValueError(
                "similarity_threshold must be between 0.0 and 1.0."
            )

        self._embedder = embedder
        self._vector_store = vector_store
        self._similarity_threshold = similarity_threshold

        logger.info(
            "SimilarityDetector initialized "
            "(threshold=%.2f).",
            self._similarity_threshold,
        )


    def detect(
        self,
        context: SecurityContext,
    ) -> ValidationResult:

        logger.info(
            "Running semantic similarity detection."
        )

        try:

            # -------------------------------------------------
            # Step 1 : Generate query embedding
            # -------------------------------------------------

            query_embedding = self._embedder.embed_query(
                context.query
            )

            # -------------------------------------------------
            # Step 2 : Search attack collection
            # -------------------------------------------------

            results = self._vector_store.search(
                embedding=query_embedding,
                top_k=1,
            )

            # -------------------------------------------------
            # Step 3 : No results
            # -------------------------------------------------

            if (
                not results["ids"]
                or not results["ids"][0]
            ):
                logger.info(
                    "No semantic attack match found."
                )

                return self._build_safe_result()

            # -------------------------------------------------
            # Step 4 : Extract best match
            # -------------------------------------------------

            metadata = results["metadatas"][0][0]

            document = results["documents"][0][0]

            distance = results["distances"][0][0]

            similarity = self._calculate_similarity(
                distance
            )

            logger.info(
                "Semantic similarity = %.3f",
                similarity,
            )

            # -------------------------------------------------
            # Step 5 : Threshold check
            # -------------------------------------------------

            if similarity < self._similarity_threshold:

                logger.info(
                    "Similarity below threshold."
                )

                return self._build_safe_result()

            # -------------------------------------------------
            # Step 6 : Attack detected
            # -------------------------------------------------

            return self._build_flagged_result(
                similarity=similarity,
                metadata=metadata,
                matched_text=document,
            )

        except Exception:

            logger.exception(
                "Semantic detection failed."
            )

            raise
    def _calculate_similarity(
        self,
        distance: float,
    ) -> float:

        similarity = 1.0 - distance

        similarity = max(
            0.0,
            min(1.0, similarity),
        )

        logger.debug(
            "Distance %.4f converted to similarity %.4f.",
            distance,
            similarity,
        )

        return similarity

    def _build_safe_result(
        self,
    ) -> ValidationResult:


        return ValidationResult(
            detector_name="SimilarityDetector",
            category=AttackCategory.BENIGN,
            is_flagged=False,
            confidence=0.0,
            reason="No semantically similar attack detected.",
        )
    
    def _build_flagged_result(
        self,
        similarity: float,
        metadata: dict,
        matched_text: str,
    ) -> ValidationResult:
    

        category = AttackCategory(
            metadata["attack_category"]
        )

        match = DetectionMatch(
            matched_text=matched_text,
            pattern_name="semantic_similarity",
        )

        return ValidationResult(
            detector_name="SimilarityDetector",
            category=category,
            is_flagged=True,
            confidence=similarity,
            reason=(
                "Query is semantically similar "
                "to a known attack."
            ),
            matches=[match],
        )