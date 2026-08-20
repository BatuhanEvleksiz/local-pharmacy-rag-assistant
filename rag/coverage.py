from __future__ import annotations

from rag.retriever import (
    RetrievedChunk,
    normalize_query_text,
    normalized_tokens,
    query_terms,
)


CLINICAL_DETAIL_TERMS = [
    "yan etki",
    "yan etkileri",
    "advers",
    "kontrendikasyon",
    "kullanmadan once",
    "kullanmadan önce",
    "nasil kullanilir",
    "nasıl kullanılır",
    "doz",
    "gebelik",
    "emzirme",
    "saklama",
]

LIST_SOURCE_FILES = {
    "ruhsatli_beseri_tibbi_urunler.txt",
    "e_recete_ilac_listesi.txt",
}


def asks_for_clinical_detail(question: str) -> bool:
    normalized = normalize_query_text(question)
    return any(term in normalized for term in CLINICAL_DETAIL_TERMS)


def only_list_sources(chunks: list[RetrievedChunk]) -> bool:
    return bool(chunks) and all(chunk.source_file in LIST_SOURCE_FILES for chunk in chunks)


def filter_chunks_by_query_terms(
    question: str,
    chunks: list[RetrievedChunk],
) -> list[RetrievedChunk]:
    terms = query_terms(question)
    if not terms:
        return chunks

    filtered = [
        chunk
        for chunk in chunks
        if any(term in normalized_tokens(chunk.text) for term in terms)
    ]
    return filtered or chunks
