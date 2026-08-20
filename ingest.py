from __future__ import annotations

import logging

from rag.chunker import chunk_documents
from rag.config import get_settings
from rag.document_loader import load_documents
from rag.logging_utils import configure_logging
from rag.vector_store import EmbeddingModel, VectorStore


logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.docs_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading documents from %s", settings.docs_dir)
    documents = load_documents(settings.docs_dir)
    if not documents:
        logger.warning("No supported documents found in %s", settings.docs_dir)
        logger.warning("Run scripts/fetch_titck_data.py or add .pdf, .txt, .md files.")
        return

    chunks = chunk_documents(documents)
    logger.info("Loaded %s documents and built %s chunks", len(documents), len(chunks))

    embedding_model = EmbeddingModel(settings)
    logger.info("Using embedding model: %s", embedding_model.model_name)
    embeddings = embedding_model.encode([chunk.text for chunk in chunks])

    vector_store = VectorStore(settings)
    vector_store.reset()
    vector_store.add_chunks(chunks, embeddings)

    logger.info("Ingestion complete")
    logger.info("Documents: %s", len(documents))
    logger.info("Chunks: %s", len(chunks))
    logger.info("Chroma collection: %s", settings.collection_name)


if __name__ == "__main__":
    main()
