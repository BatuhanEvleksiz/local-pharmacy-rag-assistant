from __future__ import annotations

from rag.chunker import chunk_documents
from rag.config import get_settings
from rag.document_loader import load_documents
from rag.vector_store import EmbeddingModel, VectorStore


def main() -> None:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.docs_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(settings.docs_dir)
    if not documents:
        print(f"No supported documents found in {settings.docs_dir}")
        print("Add .pdf, .txt, or .md files and run ingestion again.")
        return

    chunks = chunk_documents(documents)
    embedding_model = EmbeddingModel(settings)
    embeddings = embedding_model.encode([chunk.text for chunk in chunks])

    vector_store = VectorStore(settings)
    vector_store.reset()
    vector_store.add_chunks(chunks, embeddings)

    print("Ingestion complete.")
    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embedding model: {embedding_model.model_name}")
    print(f"Chroma collection: {settings.collection_name}")


if __name__ == "__main__":
    main()
