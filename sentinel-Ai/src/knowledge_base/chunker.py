from __future__ import annotations

import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.knowledge_base.models import Document,Chunk
from pathlib import Path

logger = logging.getLogger(__name__)

class TextChunker:

    def __init__(self,chunk_size:int = 1000,chunk_overlap: int = 200):

        if chunk_size <=0:
            raise ValueError(
                "Chunk size must be greater that zero"
            )
        if chunk_overlap < 0:
            raise ValueError(
                "Chunk overlap must be greater that zero"
            )
        
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap should be less than the chunk_size"
            )
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            length_function = len,
            is_separator_regex= False,
        )

        logger.info(
            "TextChunker Initalized"
            "(chunk_size = %d,overlap = %d)",
            self.chunk_size,self.chunk_overlap,
        )
        
    def chunk_documents(self,documents: list[Document])->list[Chunk]:


        chunks : list[Chunk] = []
        logger.info(
            "Starting Chunking of %d documents",
            len(documents)
        )

        for document in documents:
            chunks.extend(
                self._chunk_document(document)

            )

        logger.info(
            "Generated %d chunks",
            len(chunks),
        )

        return chunks
    def _chunk_document(self, document: Document) -> list[Chunk]:


        chunk_texts = self.splitter.split_text(
            document.content
        )

        # FIX 4C — Chunk size guard: re-split oversized chunks by sentence boundary.
        _MAX_CHUNK_CHARS = 2000
        final_texts: list[str] = []
        for raw_text in chunk_texts:
            if len(raw_text) <= _MAX_CHUNK_CHARS:
                final_texts.append(raw_text)
            else:
                # Greedy sentence-boundary split on ". "
                sentences = raw_text.split(". ")
                current: list[str] = []
                current_len = 0
                for sentence in sentences:
                    # +2 for ". " rejoining separator
                    added_len = len(sentence) + (2 if current else 0)
                    if current_len + added_len > _MAX_CHUNK_CHARS and current:
                        final_texts.append(". ".join(current))
                        current = [sentence]
                        current_len = len(sentence)
                    else:
                        current.append(sentence)
                        current_len += added_len
                if current:
                    final_texts.append(". ".join(current))

        logger.debug(
            "Generated %d chunks from %s",
            len(final_texts),
            document.metadata["document_name"],
        )

        chunks: list[Chunk] = []

        for index, chunk_text in enumerate(
            final_texts,
            start=1,
        ):
            
            chunks.append(
                self._build_chunk(
                    document=document,
                    chunk_text=chunk_text,
                    chunk_index=index,
                )
            )

        return chunks
    def _build_chunk(
            self,document:Document,
            chunk_text :str,
            chunk_index: int,)-> Chunk:
        
        metadata = {
            **document.metadata,
            "chunk_id": self._generate_chunk_id(
            document.metadata,
            chunk_index,
            ),
            "chunk_length": len(chunk_text),
        }

        return Chunk(
            content=chunk_text,
            metadata=metadata
        )
    
    @staticmethod
    def _generate_chunk_id(metadata: dict[str,object],
                           chunk_index:int,)->str:
        
        domain = str(metadata.get("domain","general"))
        document_name = str(metadata["document_name"])

        document_stem = Path(document_name).stem

        return(
            f"{domain}_"
            f"{document_stem}_"
            f"{chunk_index:03d}"
        )