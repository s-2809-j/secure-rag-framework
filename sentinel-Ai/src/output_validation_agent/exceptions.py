from __future__ import annotations


class OutputValidationError(Exception):
    """
    Base exception for all Output Validation Agent errors.
    """


class ValidatorExecutionError(OutputValidationError):
    """
    Raised when a validator fails during execution.
    """

class InvalidValidationResultError(
    OutputValidationError
):
    """
    Raised when a validator returns an invalid
    ValidationResult.
    """
    
class PolicyEvaluationError(OutputValidationError):
    """
    Raised when the policy engine fails.
    """


class RiskAssessmentError(OutputValidationError):
    """
    Raised when the risk engine fails.
    """


class InvalidValidationContextError(OutputValidationError):
    """
    Raised when an invalid ValidationContext is supplied.
    """


class InvalidValidationDecisionError(OutputValidationError):
    """
    Raised when the Output Validation Agent produces an
    invalid ValidationDecision.
    """

class Tier2JudgeError(OutputValidationError):
    """
    Base exception for Tier-2 Judge failures.
    """


class InvalidTier2ResponseError(Tier2JudgeError):
    """
    Raised when the LLM returns an invalid response.
    """


class LLMInvocationError(Tier2JudgeError):
    """
    Raised when the Tier-2 LLM invocation fails.
    """

class SanitizationError(OutputValidationError):
    """
    Raised when response sanitization fails.
    """
