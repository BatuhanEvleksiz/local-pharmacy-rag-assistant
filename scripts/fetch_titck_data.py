from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from rag.logging_utils import configure_logging


logger = logging.getLogger(__name__)


IMPORTANT_COLUMN_KEYS = {
    "sira no",
    "barkod",
    "urun adi",
    "ilac adi",
    "etkin madde",
    "etkin madde adi",
    "atc kodu",
    "atc adi",
    "firma adi",
    "ruhsat sahibi",
    "ruhsat tarihi",
    "ruhsat numarasi",
    "recete turu",
    "durumu",
    "aciklama",
}


TITCK_BASE = "https://www.titck.gov.tr"


@dataclass(frozen=True)
class SourceList:
    slug: str
    page_url: str
    title: str
    source_note: str


SOURCES = [
    SourceList(
        slug="ruhsatli_beseri_tibbi_urunler",
        page_url=f"{TITCK_BASE}/dinamikmodul/85",
        title="TITCK Ruhsatli Beseri Tibbi Urunler Listesi",
        source_note="TITCK Ruhsatli Urunler Listesi",
    ),
    SourceList(
        slug="e_recete_ilac_listesi",
        page_url=f"{TITCK_BASE}/dinamikmodul/43",
        title="TITCK SKRS E-Recete Ilac ve Diger Farmasotik Urunler Listesi",
        source_note="TITCK SKRS E-Recete Ilac Listesi",
    ),
]


def find_latest_xlsx_url(html: str, page_url: str) -> str:
    match = re.search(r'href="([^"]+\.xlsx[^"]*)"', html, flags=re.IGNORECASE)
    if not match:
        raise RuntimeError(f"No XLSX link found on {page_url}")
    return urljoin(page_url, match.group(1).replace("&amp;", "&"))


def download_latest_xlsx(source: SourceList, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    logger.info("Opening source page: %s", source.page_url)
    html_response = session.get(source.page_url, timeout=30)
    html_response.raise_for_status()
    xlsx_url = find_latest_xlsx_url(html_response.text, source.page_url)

    output_path = output_dir / f"{source.slug}.xlsx"
    logger.info("Downloading latest XLSX: %s", xlsx_url)
    response = session.get(xlsx_url, timeout=120)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_header(value: object) -> str:
    return clean_cell(value).replace("\n", " ").strip()


def normalize_key(value: object) -> str:
    text = normalize_header(value).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    table = str.maketrans("çğıöşü", "cgiosu")
    return text.translate(table)


def find_header_row(raw_frame: pd.DataFrame) -> int:
    header_markers = {"ilac adi", "urun adi", "barkod", "etkin madde", "etkin madde adi"}
    best_index = 0
    best_score = 0

    for index, row in raw_frame.iterrows():
        cells = {normalize_key(value) for value in row.tolist()}
        score = len(header_markers.intersection(cells))
        if score > best_score:
            best_index = int(index)
            best_score = score

    return best_index if best_score >= 2 else 0


def parse_sheet(excel: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    raw = excel.parse(sheet_name=sheet_name, header=None)
    raw = raw.dropna(how="all")
    if raw.empty:
        return pd.DataFrame()

    header_row = find_header_row(raw)
    headers = [normalize_header(value) for value in raw.iloc[header_row].tolist()]
    data = raw.iloc[header_row + 1 :].copy()
    data.columns = headers
    data = data.dropna(how="all")
    data = data.loc[:, [bool(str(column).strip()) for column in data.columns]]
    data = data.loc[:, ~data.columns.duplicated()]
    data = data.drop(
        columns=[
            column
            for column in data.columns
            if clean_cell(column).lower().startswith("nan")
            or clean_cell(column).lower().startswith("unnamed")
        ],
        errors="ignore",
    )
    return data


def row_to_text(row: pd.Series, source: SourceList, row_number: int) -> str:
    parts: list[str] = []
    for column, value in row.items():
        column_text = clean_cell(column)
        value_text = clean_cell(value)
        normalized_column = normalize_key(column_text)
        is_important = normalized_column in IMPORTANT_COLUMN_KEYS
        if (
            column_text
            and value_text
            and is_important
            and not column_text.lower().startswith("unnamed")
        ):
            parts.append(f"{column_text}: {value_text}")

    if not parts:
        values = [clean_cell(value) for value in row.tolist()]
        parts = [value for value in values if value]

    return (
        f"KAYNAK: {source.source_note}\n"
        f"KAYIT NO: {row_number}\n"
        + "\n".join(parts)
    )


def xlsx_to_corpus(source: SourceList, xlsx_path: Path, output_dir: Path) -> tuple[Path, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Reading workbook: %s", xlsx_path)
    excel = pd.ExcelFile(xlsx_path)
    blocks: list[str] = [
        f"ILAC ADI: {source.title}",
        f"KAYNAK: {source.page_url}",
        "Bu dosya resmi TİTCK listelerinden yerel RAG korpusu icin uretilmistir.",
    ]

    row_number = 0
    for sheet_name in excel.sheet_names:
        frame = parse_sheet(excel, sheet_name)
        for _, row in frame.iterrows():
            text = row_to_text(row, source, row_number=row_number + 1)
            if len(text.strip()) > 40:
                blocks.append(f"SAYFA: {sheet_name}\n{text}")
                row_number += 1

    output_path = output_dir / f"{source.slug}.txt"
    output_path.write_text("\n\n".join(blocks), encoding="utf-8")
    return output_path, row_number


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="Download official TITCK XLSX lists and build local RAG corpus."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=ROOT_DIR / "data_sources",
        help="Directory for downloaded XLSX files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "real_docs",
        help="Directory for generated corpus text files.",
    )
    args = parser.parse_args()

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [],
    }

    for source in SOURCES:
        logger.info("Processing source: %s", source.title)
        xlsx_path = download_latest_xlsx(source, args.source_dir)
        corpus_path, row_count = xlsx_to_corpus(source, xlsx_path, args.output_dir)
        manifest["sources"].append(
            {
                "slug": source.slug,
                "title": source.title,
                "page_url": source.page_url,
                "xlsx_path": str(xlsx_path),
                "corpus_path": str(corpus_path),
                "rows": row_count,
            }
        )
        logger.info("Saved XLSX: %s", xlsx_path)
        logger.info("Generated corpus: %s (%s rows)", corpus_path, row_count)

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Generated manifest: %s", manifest_path)


if __name__ == "__main__":
    main()
