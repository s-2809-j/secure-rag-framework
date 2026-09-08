from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from src.output_validation_agent.exceptions import (
    InvalidValidationContextError,
    InvalidValidationResultError,
    ValidatorExecutionError,
)
from src.output_validation_agent.models import (
    ValidationContext,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Abstract base class for all output validators.

    This class implements the Template Method pattern.
    Subclasses should implement only the `_validate()` method.
    """

    def __init__(self) -> None:
        self._name = self.__class__.__name__

    @property
    def name(self) -> str:
        """
        Returns the validator name.
        """
        return self._name

    def validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Execute the validator.

        This method should not be overridden by subclasses.
        """

        if not isinstance(context, ValidationContext):
            raise InvalidValidationContextError(
                "Expected a ValidationContext instance."
            )

        logger.info(
            "Running validator '%s'.",
            self._name,
        )

        try:
            result = self._validate(context)

            if not isinstance(result, ValidationResult):
                raise InvalidValidationResultError(
                    f"Validator '{self._name}' returned an invalid "
                    "ValidationResult."
                )

        except (
            InvalidValidationContextError,
            InvalidValidationResultError,
        ):
            raise

        except Exception as exc:
            logger.exception(
                "Validator '%s' failed.",
                self._name,
            )

            raise ValidatorExecutionError(
                f"Validator '{self._name}' failed."
            ) from exc

        logger.info(
            "Validator '%s' completed. "
            "Passed=%s Score=%.2f",
            self._name,
            result.passed,
            result.score,
        )

        return result

    @abstractmethod
    def _validate(
        self,
        context: ValidationContext,
    ) -> ValidationResult:
        """
        Perform validator-specific validation.

        Subclasses must implement this method and return a
        ValidationResult.
        """