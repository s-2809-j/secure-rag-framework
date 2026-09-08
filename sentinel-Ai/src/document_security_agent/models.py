from __future__ import annotations
from enum import Enum
from dataclasses import dataclass,field
from src.input_security_agent.models import ValidationResult,AttackCategory
from typing import List,Optional
from src.input_security_agent.models import (
    PolicyEvaluation,
    RiskAssessment,
)
from src.common.models import FileMetadata


@dataclass(slots=True)
class ParsedDocument:
    
    metadata: FileMetadata
    text: str
    page_count: int
    parser_name: str
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Chunk:
    """
    Represents a chunk extracted from a document.
    """

    id: int
    text: str

    start_offset: int
    end_offset: int

    metadata: dict[str, str] = field(default_factory=dict)
@dataclass(slots=True)
class ChunkedDocument:
    """
    Parsed document split into chunks.
    """

    metadata: FileMetadata

    chunks: list[Chunk]

    page_count: int

    parser_name: str

    warnings: list[str] = field(default_factory=list)

@dataclass(slots=True)
class ChunkDetectionResult:
    """
    Security analysis result for a single chunk.
    """

    chunk: Chunk
    validation_results: list[ValidationResult]

@dataclass(slots=True)
class Tier1DetectionReport:
    """
    Detection results for an entire document.
    """

    metadata: FileMetadata
    chunk_results: list[ChunkDetectionResult]

@dataclass(slots=True)
class CategorySummary:
    category: AttackCategory
    affected_chunks: list[int]
    total_matches: int
    highest_confidence: float

@dataclass(slots=True)
class DocumentStatistics:
    total_chunks: int
    flagged_chunks: int
    safe_chunks: int

@dataclass(slots=True)
class DocumentAggregationReport:
    statistics: DocumentStatistics
    category_summaries: list[CategorySummary]



class EscalationPriority(str, Enum):
    """Priority assigned to an escalated chunk."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
@dataclass(slots=True)
class EscalatedChunk:
    """
    Represents a chunk selected for Tier-2 analysis.
    """

    chunk: Chunk
    priority: EscalationPriority
    reasons: list[str] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)

@dataclass(slots=True)
class EscalationReport:
    """
    Output of the Escalation Engine.
    """

    metadata: FileMetadata
    total_chunks: int
    escalated_chunks: list[EscalatedChunk] = field(default_factory=list)
    @property
    def total_escalated_chunks(self) -> int:
        return len(self.escalated_chunks)

@dataclass(slots=True)
class Tier2ChunkResult:
    chunk: Chunk
    validation_results: list[ValidationResult]

@dataclass(slots=True)
class Tier2DetectionReport:
    metadata: FileMetadata
    chunk_results: list[Tier2ChunkResult]

@dataclass(slots=True)
class DocumentDetectionReport:
    """
    Complete detection report produced by the document
    detection pipeline.
    """

    tier1_report: Tier1DetectionReport
    escalation_report: EscalationReport | None = None
    tier2_report: Tier2DetectionReport | None = None


@dataclass(slots=True)
class DocumentDecision:

    allowed: bool
    message: str

    parsed_document: ParsedDocument

    detection_report: DocumentDetectionReport
    aggregation_report: DocumentAggregationReport

    policy_evaluation: PolicyEvaluation
    risk_assessment: RiskAssessment

    recommendations: list[str] = field(default_factory=list)
    
@dataclass(slots=True)
class DocumentParseResult:

    success: bool
    document: Optional[ParsedDocument] = None
    warnings: List[str] = field(default_factory=list)