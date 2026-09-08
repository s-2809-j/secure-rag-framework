from __future__ import annotations


class SecurityAgentError(Exception):
    """Base exception for all errors raised within the security module."""


class ConfigurationError(SecurityAgentError):
    """Raised when a detector, policy, or agent is constructed with
    invalid or missing configuration (e.g. an out-of-range threshold)."""


class DetectorExecutionError(SecurityAgentError):
    """Raised when a detector fails while running -- an operational
    failure (e.g. an underlying model/service error), not a detection
    outcome. Detecting an attack is a normal ValidationResult; failing
    to run the check at all is this."""


class InvalidValidationResultError(SecurityAgentError):
    """Raised when a detector attempts to construct a ValidationResult
    that violates the shared contract (e.g. confidence outside [0, 1]).
    This indicates a bug in the detector itself."""