from __future__ import annotations

from src.document_security_agent.parser.pdf_parser import PDFParser
from src.document_security_agent.parser.docx_parser import DocxParser
from src.document_security_agent.parser.txt_parser import TxtParser
from src.document_security_agent.parser.markdown_parser import MarkdownParser


SUPPORTED_EXTENSIONS: set[str] = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


SUPPORTED_MIME_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
    ".txt": "text/plain",
    ".md": "text/markdown",
}


MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB


PARSER_MAPPING = {
    ".pdf": PDFParser(),
    ".docx": DocxParser(),
    ".txt": TxtParser(),
    ".md": MarkdownParser(),
}