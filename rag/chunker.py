from __future__ import annotations

import re
from dataclasses import dataclass

from rag.document_loader import SourceDocument


SECTION_ALIASES = {
    "kullanmadan once": [
        "kullanmadan once dikkat edilmesi gerekenler",
        "kullanmadan önce dikkat edilmesi gerekenler",
        "uyarilar",
        "uyarılar",
        "kontrendikasyon",
    ],
    "nasil kullanilir": [
        "nasil kullanilir",
        "nasıl kullanılır",
        "kullanim sekli",
        "kullanım şekli",
        "doz",
    ],
    "olasi yan etkiler": [
        "olasi yan etkiler",
        "olası yan etkiler",
        "yan etkiler",
    ],
    "saklama kosullari": [
        "saklama kosullari",
        "saklama koşulları",
        "muhafaza",
    ],
    "icerik": [
        "etkin madde",
        "yardimci maddeler",
        "yardımcı maddeler",
        "icerik",
        "içerik",
    ],
    "kullanim amaci": [
        "ne icin kullanilir",
        "ne için kullanılır",
        "endikasyon",
        "kullanim amaci",
        "kullanım amacı",
    ],
}


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source_file: str
    drug_name: str
    section: str
    chunk_index: int


def _normalize(value: str) -> str:
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return value.translate(table).lower()


def detect_section(text: str, current_section: str = "genel") -> str:
    normalized = _normalize(text)
    for section, aliases in SECTION_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return section
    return current_section


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) > 1:
        return paragraphs
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]


def _pack_paragraphs(paragraphs: list[str], max_chars: int, overlap_chars: int) -> list[str]:
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            for start in range(0, len(paragraph), max_chars - overlap_chars):
                chunks.append(paragraph[start : start + max_chars].strip())
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current.strip())
            tail = current[-overlap_chars:].strip() if overlap_chars and current else ""
            current = f"{tail}\n\n{paragraph}".strip() if tail else paragraph

    if current:
        chunks.append(current.strip())
    return chunks


def chunk_document(
    document: SourceDocument,
    max_chars: int = 950,
    overlap_chars: int = 120,
) -> list[Chunk]:
    paragraphs = _split_paragraphs(document.text)
    raw_chunks = _pack_paragraphs(paragraphs, max_chars=max_chars, overlap_chars=overlap_chars)

    chunks: list[Chunk] = []
    current_section = "genel"
    for index, text in enumerate(raw_chunks):
        current_section = detect_section(text, current_section)
        chunks.append(
            Chunk(
                id=f"{document.path.stem}-{index}",
                text=text,
                source_file=document.path.name,
                drug_name=document.drug_name,
                section=current_section,
                chunk_index=index,
            )
        )
    return chunks


def chunk_documents(documents: list[SourceDocument]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document))
    return chunks
