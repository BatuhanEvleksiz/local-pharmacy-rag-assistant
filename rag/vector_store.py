from __future__ import annotations

from dataclasses import asdict

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from rag.chunker import Chunk
from rag.config import Settings


class EmbeddingModel:
    def __init__(self, settings: Settings) -> None:
        try:
            self.model = SentenceTransformer(settings.embedding_model)
            self.model_name = settings.embedding_model
        except Exception:
            self.model = SentenceTransformer(settings.fallback_embedding_model)
            self.model_name = settings.fallback_embedding_model

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self.collection.add(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    key: value
                    for key, value in asdict(chunk).items()
                    if key not in {"id", "text"}
                }
                for chunk in chunks
            ],
        )

    def count(self) -> int:
        return self.collection.count()
