from __future__ import annotations
import logging
import unicodedata
import re


logger = logging.getLogger(__name__)

class InputNormalizer:

    _ZERO_WIDTH_PATTERN = re.compile(
         r"[\u200B\u200C\u200D\u2060\uFEFF]"
    )

    _MULTIPLE_WHITESPACE = re.compile(r"\s+")

    def normalize(
            self,
            text: str,

    )-> str:
        
        logger.info("Normalizing input query")

        normalized = text
        normalized = self._normalize_unicode(normalized)

        normalized = self._remove_zero_width(normalized)

        normalized = self._normalize_line_endings(normalized)

        normalized = self._collapse_whitespace(normalized)

        normalized = normalized.strip()  

        logger.info("Input Normalization Completed")

        return  normalized
        
    
    @staticmethod
    def _normalize_unicode(text:str)->str:

        return unicodedata.normalize(
            "NFKC",
            text,


            )
    def _remove_zero_width(
        self,
        text: str,
    ) -> str:
        return self._ZERO_WIDTH_PATTERN.sub(
            "",
            text,
        )

    @staticmethod
    def _normalize_line_endings(
        text: str,
    ) -> str:
        return (
            text.replace("\r\n", "\n")
                .replace("\r", "\n")
        )

    def _collapse_whitespace(
        self,
        text: str,
    ) -> str:
        return self._MULTIPLE_WHITESPACE.sub(
            " ",
            text,
        )