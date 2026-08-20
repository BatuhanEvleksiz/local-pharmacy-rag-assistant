from __future__ import annotations

from openai import OpenAI

from rag.config import Settings
from rag.prompts import build_context, build_messages
from rag.retriever import RetrievedChunk
from rag.safety import safety_footer


class AnswerGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.foundry_base_url,
            api_key=settings.foundry_api_key,
        )

    def answer(self, question: str, chunks: list[RetrievedChunk]) -> str:
        context = build_context(chunks, self.settings.max_context_chars)
        messages = build_messages(question, context)
        response = self.client.chat.completions.create(
            model=self.settings.foundry_model,
            messages=messages,
            temperature=0.2,
            max_tokens=450,
        )
        content = response.choices[0].message.content or ""
        return content.strip() + safety_footer()
