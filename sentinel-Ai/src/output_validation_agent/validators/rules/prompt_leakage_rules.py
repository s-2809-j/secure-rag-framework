from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from re import Pattern


class PromptLeakageType(Enum):
    SYSTEM_PROMPT = "system_prompt"
    DEVELOPER_INSTRUCTION = "developer_instruction"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TOOL_TRACE = "tool_trace"
    ARCHITECTURE_DISCLOSURE = "architecture_disclosure"
    HIDDEN_PROMPT = "hidden_prompt"


@dataclass(frozen=True, slots=True)
class PromptLeakageRule:
    """
    Represents a single prompt leakage detection rule.
    """

    name: str
    category: PromptLeakageType
    pattern: Pattern[str]
    description: str


# ---------------------------------------------------------------------------
# System Prompt Leakage Rules
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_RULES = (
    PromptLeakageRule(
        name="system_prompt",
        category=PromptLeakageType.SYSTEM_PROMPT,
        pattern=re.compile(
            r"\b(system\s+prompt|begin\s+system\s+prompt|end\s+system\s+prompt)\b",
            re.IGNORECASE,
        ),
        description="System prompt disclosure.",
    ),
    PromptLeakageRule(
        name="assistant_identity",
        category=PromptLeakageType.SYSTEM_PROMPT,
        pattern=re.compile(
            r"\byou\s+are\s+(chatgpt|an?\s+ai\s+assistant)\b",
            re.IGNORECASE,
        ),
        description="Assistant identity disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Developer Instruction Leakage Rules
# ---------------------------------------------------------------------------

DEVELOPER_INSTRUCTION_RULES = (
    PromptLeakageRule(
        name="developer_instruction",
        category=PromptLeakageType.DEVELOPER_INSTRUCTION,
        pattern=re.compile(
            r"\b("
            r"developer\s+message|"
            r"developer\s+instruction|"
            r"internal\s+instruction|"
            r"hidden\s+instruction|"
            r"follow\s+these\s+instructions"
            r")\b",
            re.IGNORECASE,
        ),
        description="Developer instruction disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Chain-of-Thought Leakage Rules
# ---------------------------------------------------------------------------

CHAIN_OF_THOUGHT_RULES = (
    PromptLeakageRule(
        name="chain_of_thought",
        category=PromptLeakageType.CHAIN_OF_THOUGHT,
        pattern=re.compile(
            r"\b("
            r"chain\s+of\s+thought|"
            r"reasoning\s+trace|"
            r"internal\s+reasoning|"
            r"assistant\s+scratchpad|"
            r"let\s+me\s+think"
            r")\b",
            re.IGNORECASE,
        ),
        description="Chain-of-thought disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Tool Trace Leakage Rules
# ---------------------------------------------------------------------------

TOOL_TRACE_RULES = (
    PromptLeakageRule(
        name="tool_trace",
        category=PromptLeakageType.TOOL_TRACE,
        pattern=re.compile(
            r"\b("
            r"tool_call|"
            r"tool_result|"
            r"function_call|"
            r"assistant_tool|"
            r"python\s+tool|"
            r"analysis\s+channel"
            r")\b",
            re.IGNORECASE,
        ),
        description="Internal tool execution disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Architecture Disclosure Rules
# ---------------------------------------------------------------------------

ARCHITECTURE_DISCLOSURE_RULES = (
    PromptLeakageRule(
        name="architecture_disclosure",
        category=PromptLeakageType.ARCHITECTURE_DISCLOSURE,
        pattern=re.compile(
            r"\b("
            r"ValidationContext|"
            r"ValidationResult|"
            r"BaseValidator|"
            r"HallucinationValidator|"
            r"PromptLeakageValidator|"
            r"PIIValidator|"
            r"SafetyPolicyValidator|"
            r"OutputValidationAgent|"
            r"OutputRiskEngine|"
            r"OutputPolicyEngine|"
            r"ResponseSanitizer|"
            r"Tier2Judge"
            r")\b",
            re.IGNORECASE,
        ),
        description="Internal Sentinel architecture disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Hidden Prompt Leakage Rules
# ---------------------------------------------------------------------------

HIDDEN_PROMPT_RULES = (
    PromptLeakageRule(
        name="hidden_prompt",
        category=PromptLeakageType.HIDDEN_PROMPT,
        pattern=re.compile(
            r"\b("
            r"hidden\s+prompt|"
            r"confidential|"
            r"internal\s+only|"
            r"do\s+not\s+reveal|"
            r"secret\s+prompt|"
            r"private\s+instruction"
            r")\b",
            re.IGNORECASE,
        ),
        description="Hidden prompt disclosure.",
    ),
)

# ---------------------------------------------------------------------------
# Aggregate Rule Collection
# ---------------------------------------------------------------------------

PROMPT_LEAKAGE_RULES = (
    *SYSTEM_PROMPT_RULES,
    *DEVELOPER_INSTRUCTION_RULES,
    *CHAIN_OF_THOUGHT_RULES,
    *TOOL_TRACE_RULES,
    *ARCHITECTURE_DISCLOSURE_RULES,
    *HIDDEN_PROMPT_RULES,
)

__all__ = [
    "PromptLeakageType",
    "PromptLeakageRule",
    "PROMPT_LEAKAGE_RULES",
]