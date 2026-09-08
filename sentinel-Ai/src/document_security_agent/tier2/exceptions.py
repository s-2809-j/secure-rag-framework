"""
Exceptions for the Tier-2 Detection Engine.
"""

from __future__ import annotations


class Tier2Error(Exception):
    """
    Base exception for all Tier-2 related errors.
    """


class Tier2DetectorError(Tier2Error):
    """
    Raised when an individual Tier-2 detector fails.
    """


class Tier2EngineError(Tier2Error):
    """
    Raised when the Tier-2 Detection Engine fails to complete.
    """


class InvalidTier2ReportError(Tier2Error):
    """
    Raised when an invalid Tier-2 report is produced.
    """