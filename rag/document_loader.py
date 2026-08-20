from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}


@dataclass(frozen=True)
class SourceDocument:
    path: Path
    title: str
    drug_name: str
    text: str


def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_pdf(path: Path) -> str:
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text(x_tolerance=1, y_tolerance=3) or "")
    return "\n\n".join(pages)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def infer_drug_name(path: Path, text: str) -> str:
    first_lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in first_lines[:8]:
        match = re.search(r"^(?:ILAC ADI|ILAÇ ADI|DRUG NAME)\s*:\s*(.+)$", line, re.I)
        if match:
            return match.group(1).strip()
    return path.stem.replace("_", " ").replace("-", " ").title()


def load_documents(docs_dir: Path) -> list[SourceDocument]:
    if not docs_dir.exists():
        return []

    documents: list[SourceDocument] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        raw_text = _read_pdf(path) if path.suffix.lower() == ".pdf" else _read_text(path)
        text = _clean_text(raw_text)
        if not text:
            continue

        documents.append(
            SourceDocument(
                path=path,
                title=path.stem,
                drug_name=infer_drug_name(path, text),
                text=text,
            )
        )
    return documents
