from __future__ import annotations

import subprocess
import sys

import streamlit as st

from rag.config import get_settings
from rag.coverage import (
    asks_for_clinical_detail,
    filter_chunks_by_query_terms,
    only_list_sources,
)
from rag.generator import AnswerGenerator
from rag.retriever import list_drugs, retrieve
from rag.safety import classify_question
from rag.vector_store import EmbeddingModel, VectorStore


st.set_page_config(
    page_title="Yerel İlaç Bilgi Asistanı",
    layout="wide",
)


@st.cache_resource(show_spinner="Modeller ve vektör veritabanı hazırlanıyor...")
def load_runtime():
    settings = get_settings()
    embedding_model = EmbeddingModel(settings)
    vector_store = VectorStore(settings)
    generator = AnswerGenerator(settings)
    return settings, embedding_model, vector_store, generator


def render_sources(chunks):
    if not chunks:
        return
    with st.expander("Kullanılan kaynak parçaları", expanded=False):
        for idx, chunk in enumerate(chunks, start=1):
            st.markdown(
                f"**{idx}. {chunk.drug_name}** - `{chunk.section}` - "
                f"`{chunk.source_file}` - skor: `{chunk.score}`"
            )
            st.caption(chunk.text[:900] + ("..." if len(chunk.text) > 900 else ""))


def run_project_command(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=get_settings().data_dir.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def render_command_result(result: subprocess.CompletedProcess[str]) -> None:
    output = "\n".join(part for part in [result.stdout, result.stderr] if part.strip())
    if result.returncode == 0:
        st.success("İşlem tamamlandı.")
    else:
        st.error(f"İşlem hata kodu ile bitti: {result.returncode}")
    if output:
        with st.expander("Komut çıktısı", expanded=result.returncode != 0):
            st.code(output[-6000:], language="text")


def render_data_tools() -> None:
    st.subheader("Veri işlemleri")
    with st.form("kubkt_download_form"):
        mode = st.segmented_control(
            "İndirme modu",
            ["Tek ilaç", "Seed listesi"],
            default="Tek ilaç",
            key="kubkt_mode",
        )
        query = st.text_input(
            "İlaç sorgusu",
            value="PAROL 500 MG TABLET",
            disabled=mode == "Seed listesi",
        )
        document_type = st.selectbox("Belge tipi", ["both", "kt", "kub"], index=0)
        submitted = st.form_submit_button("KUB/KT indir", type="primary")

    if submitted:
        if mode == "Seed listesi":
            args = [
                "scripts/fetch_kubkt_docs.py",
                "--query-file",
                "resources/kubkt_seed_products.txt",
                "--limit",
                "1",
                "--types",
                document_type,
            ]
        else:
            if not query.strip():
                st.error("İlaç sorgusu boş olamaz.")
                return
            args = [
                "scripts/fetch_kubkt_docs.py",
                "--query",
                query.strip(),
                "--limit",
                "1",
                "--types",
                document_type,
            ]
        with st.status("TITCK KUB/KT PDF'leri indiriliyor...", expanded=True) as status:
            result = run_project_command(args, timeout=420)
            render_command_result(result)
            status.update(state="complete" if result.returncode == 0 else "error")

    if st.button("Belgeleri yeniden indeksle", type="secondary"):
        with st.status("Belgeler ChromaDB'ye yeniden indeksleniyor...", expanded=True) as status:
            result = run_project_command(["ingest.py"], timeout=1200)
            render_command_result(result)
            if result.returncode == 0:
                load_runtime.clear()
                status.update(state="complete")
                st.rerun()
            status.update(state="error")


def build_local_fallback_answer(question, chunks) -> str:
    excerpts = []
    for chunk in filter_chunks_by_query_terms(question, chunks)[:2]:
        excerpts.append(
            f"- {chunk.drug_name}, {chunk.section}: {chunk.text[:420]}"
            + ("..." if len(chunk.text) > 420 else "")
        )
    return (
        "Bulunan kaynaklara göre ilgili bilgiler:\n\n"
        + "\n\n".join(excerpts)
        + "\n\nNot: Bu yanıt yalnızca indekslenen belge metinlerinden derlenmiştir; "
        "doktor veya eczacı danışmanlığının yerine geçmez."
    )


def main() -> None:
    settings, embedding_model, vector_store, generator = load_runtime()

    st.title("Yerel İlaç Bilgi Asistanı")
    st.caption(
        "Yüklenen prospektüs/kullanma talimatı metinlerinden kaynaklı bilgi verir. "
        "Teşhis, tedavi veya doz tavsiyesi vermez."
    )

    with st.sidebar:
        st.header("Bilgi tabanı")
        count = vector_store.count()
        st.metric("İndeksli parça", count)
        st.caption(f"Belge klasörü: `{settings.docs_dir}`")
        drugs = ["Tüm belgeler"] + list_drugs(vector_store)
        selected_drug = st.selectbox("İlaç filtresi", drugs, index=0)
        st.divider()
        render_data_tools()
        st.divider()
        st.warning(
            "Bu uygulama bilgi amaçlıdır. Sağlık kararlarınız için doktor veya eczacıya danışın."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input("Örn: Bu ilacın olası yan etkileri nelerdir?")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        decision = classify_question(question)
        if not decision.allowed:
            answer = decision.message or "Bu soruya güvenli şekilde yanıt veremem."
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
            return

        if vector_store.count() == 0:
            answer = "Henüz indekslenmiş belge yok. Önce `python ingest.py` çalıştırın."
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
            return

        with st.spinner("Belgelerde ilgili kısımlar aranıyor..."):
            chunks = retrieve(
                question=question,
                settings=settings,
                embedding_model=embedding_model,
                vector_store=vector_store,
                drug_filter=selected_drug,
            )

        if not chunks or chunks[0].score < settings.min_relevance_score:
            answer = (
                "Yüklenen belgelerde bu soruya güvenilir cevap bulamadım.\n\n"
                "Not: Bu uygulama bilgi amaçlıdır; doktor veya eczacı danışmanlığının "
                "yerine geçmez."
            )
            st.markdown(answer)
            render_sources(chunks)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": chunks}
            )
            return

        if asks_for_clinical_detail(question) and only_list_sources(chunks):
            answer = (
                "Bu soru yan etki, kullanım talimatı veya benzeri klinik detay gerektiriyor. "
                "Şu an indeksli resmi TİTCK ürün listeleri ürün adı, barkod, etkin madde, "
                "ATC, firma ve ruhsat bilgisi gibi kayıt bilgilerini içeriyor; yan etki "
                "metni içermiyor.\n\n"
                "Bu yüzden bu klinik detay için güvenilir cevap veremem. Bu cevap "
                "için ilgili KÜB/KT veya kullanma talimatı PDF'i `real_docs/` klasörüne "
                "eklenip `python ingest.py` yeniden çalıştırılmalı."
            )
            st.markdown(answer)
            render_sources(filter_chunks_by_query_terms(question, chunks))
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": filter_chunks_by_query_terms(question, chunks),
                }
            )
            return

        try:
            with st.spinner("Yerel model yanıt üretiyor..."):
                answer = generator.answer(question, chunks)
        except Exception:
            answer = build_local_fallback_answer(question, chunks)

        st.markdown(answer)
        render_sources(chunks)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": chunks}
        )

main()
