from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from rag.logging_utils import configure_logging


logger = logging.getLogger(__name__)

KUBKT_PAGE_URL = "https://www.titck.gov.tr/kubkt"
KUBKT_ENDPOINT_URL = "https://www.titck.gov.tr/getkubktviewdatatable"


def extract_token(html: str) -> str:
    match = re.search(r'_token:\s*"([^"]+)"', html)
    if not match:
        raise RuntimeError("Could not find CSRF token on TITCK KUB/KT page.")
    return match.group(1)


def extract_pdf_url(html: str) -> str | None:
    match = re.search(r'href="([^"]+\.pdf)"', html)
    if not match:
        return None
    return match.group(1).replace("\\/", "/")


def safe_filename(value: str) -> str:
    value = unquote(value)
    value = re.sub(r"[^\w\s().%-]+", "_", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "_", value.strip())
    return value[:180]


def datatables_payload(token: str, query: str, limit: int) -> dict[str, str]:
    payload: dict[str, str] = {
        "draw": "1",
        "start": "0",
        "length": str(limit),
        "_token": token,
        "search[value]": query,
        "search[regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
    }
    columns = [
        "name",
        "element",
        "firmName",
        "confirmationDateKub",
        "confirmationDateKt",
        "documentPathKub",
        "documentPathKt",
    ]
    for index, column in enumerate(columns):
        payload[f"columns[{index}][data]"] = column
        payload[f"columns[{index}][searchable]"] = "true"
        payload[f"columns[{index}][orderable]"] = "true"
        payload[f"columns[{index}][search][value]"] = ""
        payload[f"columns[{index}][search][regex]"] = "false"
    return payload


def search_kubkt(query: str, limit: int) -> list[dict[str, str]]:
    session = requests.Session()
    page_response = session.get(KUBKT_PAGE_URL, timeout=30)
    page_response.raise_for_status()
    token = extract_token(page_response.text)

    response = session.post(
        KUBKT_ENDPOINT_URL,
        data=datatables_payload(token, query, limit),
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": KUBKT_PAGE_URL,
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("data", [])


def download_pdf(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="Download official TITCK KUB/KT PDFs for a product query."
    )
    parser.add_argument("--query", required=True, help="Product search query, e.g. PAROL 500 MG TABLET.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum product rows to download.")
    parser.add_argument(
        "--types",
        choices=["kub", "kt", "both"],
        default="both",
        help="Which document type to download.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "real_docs" / "kubkt",
        help="Directory for downloaded PDFs.",
    )
    args = parser.parse_args()

    rows = search_kubkt(args.query, args.limit)
    logger.info("Found %s KUB/KT rows for query: %s", len(rows), args.query)
    for row in rows:
        product_name = row.get("name", "unknown_product")
        documents: list[tuple[str, str | None]] = []
        if args.types in {"kub", "both"}:
            documents.append(("kub", extract_pdf_url(row.get("documentPathKub", ""))))
        if args.types in {"kt", "both"}:
            documents.append(("kt", extract_pdf_url(row.get("documentPathKt", ""))))

        for doc_type, url in documents:
            if not url:
                logger.warning("No %s PDF found for %s", doc_type.upper(), product_name)
                continue
            filename = f"{safe_filename(product_name)}_{doc_type}.pdf"
            output_path = args.output_dir / filename
            logger.info("Downloading %s for %s", doc_type.upper(), product_name)
            download_pdf(url, output_path)
            logger.info("Saved: %s", output_path)


if __name__ == "__main__":
    main()
