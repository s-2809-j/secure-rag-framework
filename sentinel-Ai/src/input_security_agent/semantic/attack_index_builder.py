from __future__ import annotations

import logging

from pathlib import Path

from src.input_security_agent.loader.attack_pack_loader import AttackPackLoader
from src.knowledge_base.chunker import TextChunker
from src.knowledge_base.embedder import Embedder
from src.knowledge_base.vector_store import VectorStore

logger = logging.getLogger(__name__)

class AttackIndexBuilder:

    def __init__(
        self,
        attack_pack_path : str | Path,
        loader: AttackPackLoader,
        chunker: TextChunker,
        embedder: Embedder,
        vector_store: VectorStore) -> None:
    
        self._attack_pack_path = Path(attack_pack_path)
        self._loader = loader
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store
        
    def build(self) -> None:
    

        logger.info("Building semantic attack index...")

        try:

       
            logger.info("Loading attack packs...")

            documents = self._loader.load()

            if not documents:
             raise RuntimeError(
                "No attack pack documents were found."
            )

            logger.info(
            "Loaded %d markdown documents.",
            len(documents),
        )

       
            logger.info("Chunking attack documents...")

            chunks = self._chunker.chunk_documents(
            documents
        )
            for chunk in chunks:

                source = Path(
                chunk.metadata["source"]
                )

                attack_category = source.parent.name

                chunk.metadata["attack_category"] = attack_category

                chunk.metadata["attack_pack"] = source.parent.name

            if not chunks:
                raise RuntimeError(
                "No chunks were generated."
            )

            logger.info(
            "Generated %d chunks.",
            len(chunks),
        )

      

            logger.info("Generating embeddings...")

            embedded_chunks = self._embedder.embed(
         chunks
        )

            if not embedded_chunks:
                raise RuntimeError(
                "No embeddings were generated."
            )

            logger.info(
            "Generated %d embeddings.",
            len(embedded_chunks),
        )

            logger.info(
            "Storing attack embeddings..."
        )

            self._vector_store.store(
            embedded_chunks
        )

            logger.info(
            "Semantic attack index built successfully."
        )

        except Exception:

            logger.exception(
            "Failed to build semantic attack index."
            )
            raise  
