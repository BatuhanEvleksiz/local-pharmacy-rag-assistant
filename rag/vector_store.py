from __future__ import annotations

import logging
from dataclasses import asdict

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from rag.chunker import Chunk
from rag.config import Settings


logger = logging.getLogger(__name__)


class EmbeddingModel:
    def __init__(self, settings: Settings) -> None:
        try:
            self.model = self._load(settings.embedding_model)
            self.model_name = settings.embedding_model
        except Exception as primary_error:
            logger.warning(
                "Could not load embedding model %s: %s",
                settings.embedding_model,
                primary_error,
            )
            self.model = self._load(settings.fallback_embedding_model)
            self.model_name = settings.fallback_embedding_model

    @staticmethod
    def _load(model_name: str) -> SentenceTransformer:
        try:
            return SentenceTransformer(model_name, local_files_only=True)
        except Exception as local_error:
            logger.info(
                "Embedding model %s was not fully available in local cache: %s",
                model_name,
                local_error,
            )
            return SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.collection_name = settings.collection_name
        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection_metadata = {"hnsw:space": "cosine"}

    @property
    def collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata=self._collection_metadata,
        )

    def _delete_collection_if_exists(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as error:
            logger.info("Chroma collection %s was not present: %s", self.collection_name, error)

    def reset(self) -> None:
        self._delete_collection_if_exists()
        self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )


    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        batch_size: int = 1000,
    ) -> None:
        if not chunks:
            return
        for start in range(0, len(chunks), batch_size):
            batch_chunks = chunks[start : start + batch_size]
            batch_embeddings = embeddings[start : start + batch_size]
            self.collection.add(
                ids=[chunk.id for chunk in batch_chunks],
                documents=[chunk.text for chunk in batch_chunks],
                embeddings=batch_embeddings,
                metadatas=[
                    {
                        key: value
                        for key, value in asdict(chunk).items()
                        if key not in {"id", "text"}
                    }
                    for chunk in batch_chunks
                ],
            )

    def count(self) -> int:
        return self.collection.count()
