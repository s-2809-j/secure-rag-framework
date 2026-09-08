from __future__ import annotations

import logging

from src.document_security_agent.models import (
    ChunkDetectionResult,
    ChunkedDocument,
    Tier1DetectionReport,
)
from src.input_security_agent.detectors.base import BaseDetector
from src.input_security_agent.models import SecurityContext

logger = logging.getLogger(__name__)


class DocumentDetectionEngine:
    """
    Executes all security detectors on every chunk of a document.

    This component is responsible only for running detectors and
    collecting their outputs. It does not perform aggregation,
    policy evaluation, or risk scoring.
    """

    def __init__(
        self,
        detectors: list[BaseDetector],
    ) -> None:
        if not detectors:
            raise ValueError(
                "At least one detector must be provided."
            )

        self._detectors = detectors

    def analyze(
        self,
        document: ChunkedDocument,
    ) -> Tier1DetectionReport:
        """
        Analyze every chunk in the document.

        Parameters
        ----------
        document:
            Chunked document ready for security analysis.

        Returns
        -------
        DocumentDetectionReport
            Detection results for every chunk.
        """

        logger.info(
            "Starting document security analysis."
        )

        logger.info(
            "Processing %d chunks.",
            len(document.chunks),
        )

        chunk_results: list[ChunkDetectionResult] = []

        total_chunks = len(document.chunks)

        for index, chunk in enumerate(
            document.chunks,
            start=1,
        ):
            logger.debug(
                "Analyzing chunk %d/%d.",
                index,
                total_chunks,
            )

            context = SecurityContext(
                query=chunk.text,
            )

            validation_results = []

            for detector in self._detectors:
                validation_results.append(
                    detector.detect(context)
                )

            chunk_results.append(
                ChunkDetectionResult(
                    chunk=chunk,
                    validation_results=validation_results,
                )
            )

        logger.info(
            "Completed document security analysis."
        )

        return Tier1DetectionReport(
            metadata=document.metadata,
            chunk_results=chunk_results,
        )