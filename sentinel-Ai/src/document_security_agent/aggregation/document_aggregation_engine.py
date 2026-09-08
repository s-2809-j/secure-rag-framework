from __future__ import annotations

import logging
from collections import defaultdict

from src.document_security_agent.models import (
    CategorySummary,
    DocumentAggregationReport,
    Tier1DetectionReport,
    DocumentStatistics,
)
from src.input_security_agent.models import AttackCategory

logger = logging.getLogger(__name__)


class DocumentAggregationEngine:
    """
    Aggregates chunk-level detection results into a
    document-level summary.

    This component does not perform policy evaluation
    or risk scoring.
    """

    def aggregate(
        self,
        report: Tier1DetectionReport,
    ) -> DocumentAggregationReport:

        logger.info(
            "Starting document aggregation."
        )

        total_chunks = len(report.chunk_results)
        flagged_chunks = 0

        category_data: dict[
            AttackCategory,
            dict[str, object],
        ] = defaultdict(
            lambda: {
                "chunks": [],
                "matches": 0,
                "confidence": 0.0,
            }
        )

        for index, chunk_result in enumerate(
            report.chunk_results,
            start=1,
        ):
            chunk_flagged = False

            for result in chunk_result.validation_results:

                if not result.is_flagged:
                    continue

                chunk_flagged = True

                data = category_data[result.category]

                data["chunks"].append(index)
                data["matches"] += 1
                data["confidence"] = max(
                    data["confidence"],
                    result.confidence,
                )

            if chunk_flagged:
                flagged_chunks += 1

        statistics = DocumentStatistics(
            total_chunks=total_chunks,
            flagged_chunks=flagged_chunks,
            safe_chunks=total_chunks - flagged_chunks,
        )

        summaries: list[CategorySummary] = []

        for category, data in category_data.items():

            summaries.append(
                CategorySummary(
                    category=category,
                    affected_chunks=data["chunks"],
                    total_matches=data["matches"],
                    highest_confidence=data["confidence"],
                )
            )

        logger.info(
            "Document aggregation completed."
        )

        return DocumentAggregationReport(
            statistics=statistics,
            category_summaries=summaries,
        )