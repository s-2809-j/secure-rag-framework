from __future__ import annotations

from src.output_validation_agent.models import OutputCategory


ALLOW = "allow"
SANITIZE = "sanitize"
BLOCK = "block"


POLICY_RULES: dict[OutputCategory, str] = {
    #
    # Safe responses.
    #
    OutputCategory.SAFE: ALLOW,

    #
    # Hallucination and unsupported claims: ALLOW at this stage.
    # Sentence-level heuristic scoring produces false positives on
    # paraphrased RAG responses. Full Tier-2 LLM judge is the correct
    # enforcement gate, not destructive sanitization.
    #
    OutputCategory.HALLUCINATION: ALLOW,       # ← was SANITIZE
    OutputCategory.UNSUPPORTED_CLAIM: ALLOW,   # ← was SANITIZE

    #
    # Response must never be returned.
    #
    OutputCategory.PROMPT_LEAKAGE: BLOCK,
    OutputCategory.PII: BLOCK,
    OutputCategory.POLICY_VIOLATION: BLOCK,
}