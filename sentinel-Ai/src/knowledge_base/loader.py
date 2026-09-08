from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path 
from typing import Any
from src.knowledge_base.models import Document

logger = logging.getLogger(__name__)



class MarkdownLoader:

    def __init__(self,domain_pack_root:str|Path):
        self.domain_pack_root = Path(domain_pack_root)

        if not self.domain_pack_root.exists():
            raise FileNotFoundError(f"Domain pack directory not found: {self.domain_pack_root}")
        
        if not self.domain_pack_root.is_dir():
            raise NotADirectoryError(f"{self.domain_pack_root} is not a directory")
    def _discover_domains(self) ->list[Path]:

        domains = [
            item 
            for item in self.domain_pack_root.iterdir()
            if item.is_dir()
        ]
        domains.sort()
        logger.info("Discovered %d domains",len(domains))
        return domains

    def load(self)-> list[Document]:

        documents: list[Document] = []
        domains = self._discover_domains()
        logger.info("Starting document loading")

        for domain in domains:
            documents.extend(
                self._load_domain(domain)
            )
        logger.info("Loaded %d documents",len(documents))

        return documents
    def _load_domain(self,domain_path: Path)-> list[Document]:

        documents : list[Document] = []
        documents_dir = domain_path/"documents"
        if not documents_dir.exists():
            logger.warning(
                "Documents directory not found: %s",
                documents_dir,
            )
            return documents
        markdown_files = sorted(documents_dir.rglob("*.md"))

        logger.info(
            "Loading %d documents from domain %s",
            len(markdown_files),domain_path.name
        )


        for file_path in markdown_files:
            try:
                document = self._load_document(file_path)
                documents.append(document)
            
            except Exception:
                logger.exception(
                "failed to load document: %s",
                 file_path
                )
        
        return documents
    
    def _load_document(self,file_path:Path)->Document:
        logger.debug("Loading Document: %s",file_path)

        content = file_path.read_text(
            encoding="utf-8"
        )

        metadata = self._build_metadata(file_path)

        return Document(
            content = content,metadata= metadata,
        )

    def _build_metadata(self,file_path:Path)-> dict[str,Any]:

        relative_path= file_path.relative_to(
            self.domain_pack_root
        )   
        parts = relative_path.parts

        metadata = {
            "domain": parts[0] if len(parts) > 0 else "unknown",
            "document_name" : file_path.name,
            "section": self._extract_section(parts),
            "source": relative_path.as_posix(),
            "malicious": False,

        }
        return metadata
    
    @staticmethod
    def _extract_section(parts: tuple[str,...])-> str:

        if len(parts)>3:
            return parts[2]
        
        return "root"
