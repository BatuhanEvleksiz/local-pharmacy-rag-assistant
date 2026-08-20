from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    docs_dir: Path = ROOT_DIR / "real_docs"
    data_dir: Path = ROOT_DIR / "data"
    chroma_dir: Path = ROOT_DIR / "data" / "chroma"
    collection_name: str = "pharmacy_leaflets"
    embedding_model: str = "intfloat/multilingual-e5-small"
    fallback_embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    foundry_base_url: str = "http://127.0.0.1:54312/v1"
    foundry_api_key: str = "test"
    foundry_model: str = "Phi-3.5-mini-instruct-generic-gpu:2"
    top_k: int = 5
    min_relevance_score: float = 0.28
    max_context_chars: int = 5200


def get_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    return Settings(
        docs_dir=Path(os.getenv("DOCS_DIR", ROOT_DIR / "real_docs")),
        data_dir=Path(os.getenv("DATA_DIR", ROOT_DIR / "data")),
        chroma_dir=Path(os.getenv("CHROMA_DIR", ROOT_DIR / "data" / "chroma")),
        collection_name=os.getenv("CHROMA_COLLECTION", "pharmacy_leaflets"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small"),
        fallback_embedding_model=os.getenv(
            "FALLBACK_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
        ),
        foundry_base_url=os.getenv("FOUNDRY_BASE_URL", "http://127.0.0.1:54312/v1"),
        foundry_api_key=os.getenv("FOUNDRY_API_KEY", "test"),
        foundry_model=os.getenv(
            "FOUNDRY_MODEL", "Phi-3.5-mini-instruct-generic-gpu:2"
        ),
        top_k=int(os.getenv("TOP_K", "5")),
        min_relevance_score=float(os.getenv("MIN_RELEVANCE_SCORE", "0.28")),
        max_context_chars=int(os.getenv("MAX_CONTEXT_CHARS", "5200")),
    )
