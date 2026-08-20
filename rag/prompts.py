from __future__ import annotations

from rag.retriever import RetrievedChunk


SYSTEM_PROMPT = """Sen yerel calisan bir eczacilik bilgi asistanisin.

Kurallar:
- Sadece verilen BAGLAM metnindeki bilgileri kullan.
- Teshis koyma, tedavi onerme, doz degisikligi tavsiye etme.
- Baglamda cevap yoksa net bicimde "Yuklenen belgelerde bu soruya guvenilir cevap bulamadim." de.
- Cevabi kisa, net ve Turkce ver.
- Belirsiz bilgileri kesinmis gibi yazma.
- Kullanici acil durum veya kisisel tibbi karar sorarsa saglik uzmanina yonlendir.
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
    user_prompt = f"""BAGLAM:
{context}

SORU:
{question}

Yanitini yalnizca BAGLAM'a dayanarak ver."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
