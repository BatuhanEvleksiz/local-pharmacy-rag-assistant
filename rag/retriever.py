from __future__ import annotations

import re
from dataclasses import dataclass

from rag.config import Settings
from rag.vector_store import EmbeddingModel, VectorStore


SECTION_KEYWORDS = {
    "olasi yan etkiler": ["yan etki", "alerji", "reaksiyon", "belirti"],
    "nasil kullanilir": ["doz", "kac", "kaç", "nasil kullan", "nasıl kullan", "gunde"],
    "kullanmadan once": ["hamile", "gebelik", "emzir", "kullanabilir miyim", "sakinca"],
    "saklama kosullari": ["sakla", "muhafaza", "sicaklik", "sıcaklık"],
    "icerik": ["etken", "etkin", "madde", "icerik", "içerik"],
    "kullanim amaci": ["ne icin", "ne için", "hangi hastalik", "endikasyon"],
}


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    score: float
    source_file: str
    drug_name: str
    section: str
    chunk_index: int


def infer_section_hint(question: str) -> str | None:
    normalized = question.lower()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return section
    return None


def _normalize_drug(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def _question_mentions_drug(question: str, drug_name: str) -> bool:
    normalized_question = _normalize_drug(question)
    normalized_drug = _normalize_drug(drug_name)
    if normalized_drug and normalized_drug in normalized_question:
        return True
    tokens = [token for token in re.split(r"\W+", normalized_drug) if len(token) >= 4]
    return bool(tokens) and all(token in normalized_question for token in tokens[:2])


def retrieve(
    question: str,
    settings: Settings,
    embedding_model: EmbeddingModel,
    vector_store: VectorStore,
    drug_filter: str | None = None,
) -> list[RetrievedChunk]:
    query_embedding = embedding_model.encode([question])[0]
    where = None
    if drug_filter and drug_filter != "Tum belgeler":
        where = {"drug_name": drug_filter}

    result = vector_store.collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.top_k * 2,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    section_hint = infer_section_hint(question)
    chunks: list[RetrievedChunk] = []
    for text, metadata, distance in zip(
        result.get("documents", [[]])[0],
        result.get("metadatas", [[]])[0],
        result.get("distances", [[]])[0],
    ):
        base_score = max(0.0, 1.0 - float(distance))
        section = str(metadata.get("section", "genel"))
        score = base_score
        if section_hint and section == section_hint:
            score += 0.08
        if _question_mentions_drug(question, str(metadata.get("drug_name", ""))):
            score += 0.14
        if drug_filter and drug_filter != "Tum belgeler":
            score += 0.04

        chunks.append(
            RetrievedChunk(
                text=text,
                score=round(score, 4),
                source_file=str(metadata.get("source_file", "")),
                drug_name=str(metadata.get("drug_name", "")),
                section=section,
                chunk_index=int(metadata.get("chunk_index", 0)),
            )
        )

    chunks.sort(key=lambda item: item.score, reverse=True)
    return chunks[: settings.top_k]


def list_drugs(vector_store: VectorStore) -> list[str]:
    data = vector_store.collection.get(include=["metadatas"])
    names = {
        metadata.get("drug_name")
        for metadata in data.get("metadatas", [])
        if metadata and metadata.get("drug_name")
    }
    return sorted(str(name) for name in names)
