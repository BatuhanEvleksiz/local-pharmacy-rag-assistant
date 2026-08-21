from __future__ import annotations

import json
import sys
from pathlib import Path

from rag.config import ROOT_DIR, get_settings
from rag.retriever import retrieve
from rag.safety import classify_question
from rag.vector_store import EmbeddingModel, VectorStore


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    settings = get_settings()
    vector_store = VectorStore(settings)
    embedding_model = EmbeddingModel(settings)
    questions = json.loads((ROOT_DIR / "eval_questions.json").read_text(encoding="utf-8"))

    print("Evaluation smoke report")
    print(f"Indexed chunks: {vector_store.count()}")
    print()

    for item in questions:
        decision = classify_question(item["question"])
        print(f"[{item['id']}] {item['category']}")
        print(f"Question: {item['question']}")
        print(f"Safety: {decision.category}")
        if decision.allowed and vector_store.count() > 0:
            chunks = retrieve(item["question"], settings, embedding_model, vector_store)
            top = chunks[0] if chunks else None
            if top:
                print(
                    "Top source: "
                    f"{top.drug_name} | {top.section} | {top.source_file} | score={top.score}"
                )
            else:
                print("Top source: none")
        else:
            print(f"Guardrail response: {decision.message}")
        print(f"Expected: {item['expected_behavior']}")
        print("-" * 72)


if __name__ == "__main__":
    main()
