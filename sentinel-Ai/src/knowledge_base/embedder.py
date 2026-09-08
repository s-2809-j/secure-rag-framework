from __future__ import annotations
import logging
from sentence_transformers import SentenceTransformer
from src.knowledge_base.models import Chunk,EmbeddedChunk
import numpy as np

logger = logging.getLogger(__name__)



class Embedder:
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self,model_name:str | None=None) ->None:

        self.model_name = model_name or self.DEFAULT_MODEL

        logger.info("Loading embedding model: %s",self.model_name)

        try:
            self.model = SentenceTransformer(self.model_name)

            logger.info(
                "Embedding model %s loaded successfully",
                self.model_name,
            )

        except Exception as exc:
            logger.exception("Failed to load embedding model.")

            raise RuntimeError(
                f"unable to initalize embedding model '{self.model_name}'."
            ) from exc
        
    def embed(self,chunks:list[Chunk])-> list[EmbeddedChunk]:

        if not chunks:
            logger.warning("No chunks are provided")
            return []
        
        logger.info("Generating the embedding for %d chunks",len(chunks))

        try:
            texts = [chunk.content for chunk in chunks]
            embeddings = self.model.encode(
                texts,
                convert_to_numpy = True,
                show_progress_bar = False
            )
            if len(embeddings) != len(chunks):
                raise RuntimeError(
                f"Expected {len(chunks)} embeddings but received {len(embeddings)}.")

            embedded_chunks = [
                EmbeddedChunk(
                    content = chunk.content,
                    metadata = chunk.metadata,
                    embedding=embedding,
                )
                for chunk,embedding in zip(chunks,embeddings)
            ]

            logger.info(
                "successfully generated embeddings for %d chunks",
               
                len(embedded_chunks),
            )
            return embedded_chunks
        
        except Exception as exc:

            logger.exception("Failed to generate embeddings")

            raise RuntimeError(
                "Failed to generate embeddings."
            )from exc
        
    def embed_query(self, query: str) -> np.ndarray:
        """Generate an embedding for a retrieval query (delegates to embed_text)."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        embedding = self.embed_text(query)
        # FIX 3C — Degenerate embedding guard.
        if np.all(embedding == 0.0) or np.linalg.norm(embedding) < 0.01:
            raise ValueError(
                "Degenerate embedding generated — query cannot be embedded reliably."
            )
        return embedding

    
    def embed_text(
    self,
    text: str,
) -> np.ndarray:
        """
        Generate an embedding for arbitrary text.

        Used by semantic similarity scoring and other
        validators.
        """

        if not isinstance(text, str):
            raise TypeError(
                "Text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        logger.debug(
            "Generating text embedding."
        )

        try:

            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

        except Exception as exc:

            logger.exception(
                "Failed to generate text embedding."
            )

            raise RuntimeError(
                "Failed to generate text embedding."
            ) from exc

        return embedding
            