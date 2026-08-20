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


def _is_section_heading(paragraph: str) -> bool:
    first_line = paragraph.splitlines()[0].strip()
    if re.match(r"^\d+\.\s+", first_line):
        return True
    normalized = _normalize(first_line)
    return any(
        alias in normalized
        for aliases in SECTION_ALIASES.values()
        for alias in aliases
    )


def _group_by_section(paragraphs: list[str]) -> list[tuple[str, list[str]]]:
    groups: list[tuple[str, list[str]]] = []
    current_section = "genel"
    current_paragraphs: list[str] = []

    for paragraph in paragraphs:
        if _is_section_heading(paragraph):
            if current_paragraphs:
                groups.append((current_section, current_paragraphs))
            current_section = detect_section(paragraph, current_section)
            current_paragraphs = [paragraph]
        else:
            current_section = detect_section(paragraph, current_section)
            current_paragraphs.append(paragraph)

    if current_paragraphs:
        groups.append((current_section, current_paragraphs))
    return groups


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
    max_chars: int = 3200,
    overlap_chars: int = 0,
) -> list[Chunk]:
    paragraphs = _split_paragraphs(document.text)
    chunks: list[Chunk] = []
    for section, section_paragraphs in _group_by_section(paragraphs):
        raw_chunks = _pack_paragraphs(
            section_paragraphs,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )
        for text in raw_chunks:
            index = len(chunks)
            chunks.append(
                Chunk(
                    id=f"{document.path.stem}-{index}",
                    text=text,
                    source_file=document.path.name,
                    drug_name=document.drug_name,
                    section=section,
                    chunk_index=index,
                )
            )
    return chunks


def chunk_documents(documents: list[SourceDocument]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document))
    return chunks
