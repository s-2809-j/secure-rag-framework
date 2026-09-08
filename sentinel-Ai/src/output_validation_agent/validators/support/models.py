from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class HeuristicResult:
    """
    Result produced by a single Tier-1 heuristic.

    Each heuristic independently evaluates one aspect of
    a sentence's support within the retrieved knowledge.
    """

    name: str
    applicable: bool
    score: float | None
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class HallucinationConfig:
    semantic_weight: float = 0.45
    entity_weight: float = 0.20
    numeric_weight: float = 0.20
    keyword_weight: float = 0.10
    citation_weight: float = 0.05

    high_confidence_threshold: float = 0.90
    low_confidence_threshold: float = 0.60

    enable_tier2: bool = True
    max_supporting_chunks: int = 2
    llm_confidence_threshold: float = 0.80

@dataclass(slots=True)
class SentenceEvidence:
    """
    Collection of heuristic results for a single sentence.
    """

    sentence: str
    heuristic_results: list[HeuristicResult] = field(default_factory=list)
    
@dataclass(slots=True)
class Tier2Decision:
    """
    Decision returned by the Tier-2 LLM Judge.
    """

    supported: bool
    confidence: float
    reason: str
    evidence_indices: list[int] = field(default_factory=list)

@dataclass(slots=True)
class SentenceDecision:
    """
    Final decision for a sentence after Tier-1 scoring
    and optional Tier-2 verification.
    """

    sentence: str
    support_score: float
    supported: bool
    used_tier2: bool
    tier2_decision: Tier2Decision | None = None
    evidence: SentenceEvidence | None = None

@dataclass(slots=True)
class HallucinationAggregationResult:
    """
    Aggregated statistics produced by the ResultAggregator.

    This is an internal model used only by the Hallucination
    Validator before the result is converted into the generic
    ValidationResult contract.
    """

    sentence_decisions: list[SentenceDecision]

    average_support_score: float

    confidence: float

    supported_sentence_count: int

    unsupported_sentence_count: int

    tier2_usage_count: int

    hallucination_detected: bool

    metadata: dict[str, Any] = field(default_factory=dict)
    

@dataclass(slots=True)
class EmbeddedChunk:
    """
    Text chunk with its embedding representation.
    """

    text: str
    embedding: np.ndarray
