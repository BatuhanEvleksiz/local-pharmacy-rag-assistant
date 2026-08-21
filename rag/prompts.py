from __future__ import annotations

from rag.retriever import RetrievedChunk


SYSTEM_PROMPT = """Sen yerel çalışan bir eczacılık bilgi asistanısın.

Kurallar:
- Sadece verilen BAĞLAM metnindeki bilgileri kullan.
- Teşhis koyma, tedavi önerme, doz değişikliği tavsiye etme.
- Bağlamda cevap yoksa net biçimde "Yüklenen belgelerde bu soruya güvenilir cevap bulamadım." de.
- Cevabı kısa, net ve Türkçe ver.
- Belirsiz bilgileri kesinmiş gibi yazma.
- Kullanıcı acil durum veya kişisel tıbbi karar sorarsa sağlık uzmanına yönlendir.
"""


def build_context(chunks: list[RetrievedChunk], max_chars: int) -> str:
    blocks: list[str] = []
    total = 0
    for index, chunk in enumerate(chunks, start=1):
        header = (
            f"[Kaynak {index}: {chunk.drug_name} | {chunk.section} | "
            f"{chunk.source_file} | skor={chunk.score}]"
        )
        block = f"{header}\n{chunk.text}"
        if total + len(block) > max_chars:
            break
        blocks.append(block)
        total += len(block)
    return "\n\n".join(blocks)


def build_messages(question: str, context: str) -> list[dict[str, str]]:
    user_prompt = f"""BAĞLAM:
{context}

SORU:
{question}

Yanıtını yalnızca BAĞLAM'a dayanarak ver."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
