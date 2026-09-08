from __future__ import annotations

import logging

from src.document_security_agent.document_security_pipeline import (
    DocumentSecurityPipeline,
)
from src.document_security_agent.models import (
    DocumentDecision,
    FileMetadata,
)


class DocumentSecurityAgent:
    """
    Public entry point for the Document Security subsystem.

    This class acts as a lightweight façade over the
    DocumentSecurityPipeline. It exposes a stable public API while
    delegating the complete document security workflow to the pipeline.

    Responsibilities:
        - Accept document analysis requests.
        - Delegate processing to the pipeline.
        - Provide a stable interface for external callers.

    It intentionally contains no business logic.
    """

    def __init__(
        self,
        pipeline: DocumentSecurityPipeline,
    ) -> None:
        """
        Initialize the Document Security Agent.

        Parameters
        ----------
        pipeline:
            Configured document security pipeline.
        """

        self._logger = logging.getLogger(__name__)
        self._pipeline = pipeline

    def analyze(
        self,
        file_path: str,
        metadata: FileMetadata,
    ) -> DocumentDecision:
        """
        Analyze a document using the configured security pipeline.

        Parameters
        ----------
        file_path:
            Path to the uploaded document.

        metadata:
            Metadata associated with the uploaded document.

        Returns
        -------
        DocumentDecision
            Final security decision produced by the pipeline.
        """

        self._logger.info(
            "Received document security analysis request for '%s'.",
            metadata.filename,
        )

        try:
            decision = self._pipeline.analyze(
                file_path=file_path,
                metadata=metadata,
            )

            self._logger.info(
                "Document security analysis completed. Allowed=%s",
                decision.allowed,
            )

            return decision

        except Exception:
            self._logger.exception(
                "Document security pipeline failed."
            )
            raise