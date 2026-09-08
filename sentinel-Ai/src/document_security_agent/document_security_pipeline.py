from __future__ import annotations

import logging
from src.document_security_agent.escalation import DocumentEscalationEngine
from src.document_security_agent.aggregation.document_aggregation_engine import (
    DocumentAggregationEngine,
)
from src.document_security_agent.chunking.document_chunker import (
    DocumentChunker,
)
from src.document_security_agent.detector.document_detector_engine import (
    DocumentDetectionEngine,
)
from src.document_security_agent.escalation import (
    DocumentEscalationEngine,
)
from src.document_security_agent.file_guard.file_guard import (
    FileGuard,
)
from src.document_security_agent.models import (
    DocumentDecision,
    DocumentDetectionReport,
    FileMetadata,
    ValidationResult,
)
from src.document_security_agent.parser.document_parser import (
    DocumentParser,
)
from src.document_security_agent.preprocessing.document_normalizer import (
    DocumentNormalizer,
)
from src.document_security_agent.tier2.tier2_detection_engine import (
    Tier2DetectionEngine,
)
from src.input_security_agent.policies.rule_policy_engine import (
    RulePolicyEngine,
)
from src.input_security_agent.scoring.risk_scoring_engine import (
    RiskScoringEngine,
)
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentSecurityPipeline:
    """
    Orchestrates the complete document security pipeline.
    """

    def __init__(
        self,
        file_guard: FileGuard,
        parser: DocumentParser,
        doc_normalizer: DocumentNormalizer,
        chunker: DocumentChunker,
        detection_engine: DocumentDetectionEngine,
        aggregation_engine: DocumentAggregationEngine,
        policy_engine: RulePolicyEngine,
        risk_engine: RiskScoringEngine,
        escalation_engine: DocumentEscalationEngine,
        tier2_engine: Tier2DetectionEngine,
    ) -> None:
        self._file_guard = file_guard
        self._parser = parser
        self._doc_normalizer = doc_normalizer
        self._chunker = chunker
        self._detection_engine = detection_engine
        self._aggregation_engine = aggregation_engine
        self._policy_engine = policy_engine
        self._risk_engine = risk_engine
        self._escalation_engine = escalation_engine
        self._tier2_engine = tier2_engine

    def analyze(
        self,
        file_path: str,
        metadata: FileMetadata,
    ) -> DocumentDecision:
        """
        Execute the complete document security analysis pipeline.
        """

        logger.info(
            "Starting document security analysis for '%s'.",
            metadata.filename,
        )
        try:
            # --------------------------------------------------
            # Step 1: File Validation
            # --------------------------------------------------
            file_path = Path(file_path)
            self._file_guard.validate(
                file_path
            )

            # --------------------------------------------------
            # Step 2: Document Parsing
            # --------------------------------------------------
            parse_result = self._parser.parse(
                file_path
            )

            if not parse_result.success:
                raise ValueError(
                    "Document parsing failed."
                )

            if parse_result.document is None:
                raise ValueError(
                    "Parser returned no document."
                )

            parsed_document = parse_result.document

            # --------------------------------------------------
            # Step 3: Normalization
            # --------------------------------------------------
            normalized_document = self._doc_normalizer.doc_normalize(
                parsed_document,
            )

            # --------------------------------------------------
            # Step 4: Chunking
            # --------------------------------------------------
            chunked_document = self._chunker.chunk(
                normalized_document,
            )

            # --------------------------------------------------
            # Step 5: Tier-1 Detection
            # --------------------------------------------------
            tier1_report = self._detection_engine.analyze(
                chunked_document,
            )

            # --------------------------------------------------
            # Step 6: Escalation
            # --------------------------------------------------
            escalation_report = self._escalation_engine.escalate(
                tier1_report,
            )

            # --------------------------------------------------
            # Step 7: Tier-2 Detection
            # --------------------------------------------------
            tier2_report = self._tier2_engine.analyze(
                escalation_report,
            )

            # --------------------------------------------------
            # Step 8: Detection Report
            # --------------------------------------------------
            detection_report = DocumentDetectionReport(
                tier1_report=tier1_report,
                escalation_report=escalation_report,
                tier2_report=tier2_report,
            )

            # --------------------------------------------------
            # Step 9: Aggregation
            # --------------------------------------------------
            aggregation_report = self._aggregation_engine.aggregate(
                tier1_report,
            )

            # --------------------------------------------------
            # Step 10: Collect Validation Results
            # --------------------------------------------------
            validation_results: list[ValidationResult] = []

            # Tier-1 Results
            for chunk_result in tier1_report.chunk_results:
                validation_results.extend(
                    chunk_result.validation_results
                )

            # Tier-2 Results
            for chunk_result in tier2_report.chunk_results:
                validation_results.extend(
                    chunk_result.validation_results
                )

            # --------------------------------------------------
            # Step 11: Policy Evaluation
            # --------------------------------------------------
            policy = self._policy_engine.evaluate(
                validation_results,
            )

            # --------------------------------------------------
            # Step 12: Risk Assessment
            # --------------------------------------------------
            risk = self._risk_engine.assess(
                validation_results,
            )

            logger.info(
                "Document security analysis completed successfully."
            )

            # --------------------------------------------------
            # Step 13: Final Decision
            # --------------------------------------------------
            
            return DocumentDecision(
                    allowed=policy.allowed,
                    message=policy.explanation,
                    detection_report=detection_report,
                    aggregation_report=aggregation_report,
                    policy_evaluation=policy,
                    risk_assessment=risk,
                    parsed_document=parsed_document,
                )
        except Exception:
            logger.exception("Document security pipeline failed.")
            raise