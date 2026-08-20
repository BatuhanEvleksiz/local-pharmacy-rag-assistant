from __future__ import annotations

import streamlit as st

from rag.config import get_settings
from rag.generator import AnswerGenerator
from rag.retriever import list_drugs, retrieve
from rag.safety import classify_question
from rag.vector_store import EmbeddingModel, VectorStore


st.set_page_config(
    page_title="Yerel Ilac Bilgi Asistani",
    page_icon="RX",
    layout="wide",
)


@st.cache_resource(show_spinner="Modeller ve vektor veritabani hazirlaniyor...")
def load_runtime():
    settings = get_settings()
    embedding_model = EmbeddingModel(settings)
    vector_store = VectorStore(settings)
    generator = AnswerGenerator(settings)
    return settings, embedding_model, vector_store, generator


def render_sources(chunks):
    if not chunks:
        return
    with st.expander("Kullanilan kaynak parcalari", expanded=False):
        for idx, chunk in enumerate(chunks, start=1):
            st.markdown(
                f"**{idx}. {chunk.drug_name}** - `{chunk.section}` - "
                f"`{chunk.source_file}` - skor: `{chunk.score}`"
            )
            st.caption(chunk.text[:900] + ("..." if len(chunk.text) > 900 else ""))


def main() -> None:
    settings, embedding_model, vector_store, generator = load_runtime()

    st.title("Yerel Ilac Bilgi Asistani")
    st.caption(
        "Yuklenen prospektus/kullanma talimati metinlerinden kaynakli bilgi verir. "
        "Teshis, tedavi veya doz tavsiyesi vermez."
    )

    with st.sidebar:
        st.header("Bilgi tabani")
        count = vector_store.count()
        st.metric("Indeksli parca", count)
        drugs = ["Tum belgeler"] + list_drugs(vector_store)
        selected_drug = st.selectbox("Ilac filtresi", drugs, index=0)
        st.divider()
        st.write("Veritabani bos ise once terminalden calistirin:")
        st.code("python ingest.py", language="bash")
        st.warning(
            "Bu uygulama bilgi amaclidir. Saglik kararlariniz icin doktor veya eczaciya danisin.",
            icon="!",
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input("Orn: Bu ilacin olasi yan etkileri nelerdir?")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        decision = classify_question(question)
        if not decision.allowed:
            answer = decision.message or "Bu soruya guvenli sekilde yanit veremem."
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
            return

        if vector_store.count() == 0:
            answer = "Henuz indekslenmis belge yok. Once `python ingest.py` calistirin."
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
            return

        with st.spinner("Belgelerde ilgili kisimlar araniyor..."):
            chunks = retrieve(
                question=question,
                settings=settings,
                embedding_model=embedding_model,
                vector_store=vector_store,
                drug_filter=selected_drug,
            )

        if not chunks or chunks[0].score < settings.min_relevance_score:
            answer = (
                "Yuklenen belgelerde bu soruya guvenilir cevap bulamadim.\n\n"
                "Not: Bu uygulama bilgi amaclidir; doktor veya eczaci danismanliginin "
                "yerine gecmez."
            )
            st.markdown(answer)
            render_sources(chunks)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": chunks}
            )
            return

        try:
            with st.spinner("Yerel model yanit uretuyor..."):
                answer = generator.answer(question, chunks)
        except Exception as exc:
            answer = (
                "Ilgili belge parcalari bulundu ancak yerel LLM endpoint'ine ulasilamadi. "
                "Foundry Local'in calistigindan ve `.env` ayarlarinin dogru oldugundan emin olun.\n\n"
                f"Teknik hata: `{exc}`"
            )

        st.markdown(answer)
        render_sources(chunks)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": chunks}
        )


if __name__ == "__main__":
    main()
