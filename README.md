# Yerel Eczacilik RAG Asistani

Bu proje, Microsoft Foundry Local ile yerelde calisan bir RAG asistanidir. Amac, yuklenen ilac kullanma talimati/prospektus dokumanlarindan kaynakli ve guvenli bilgi yanitlari uretmektir.

## Mimari

```text
PDF/TXT belgeler
  -> metin cikarimi
  -> bolum farkindalikli chunking
  -> sentence-transformers embedding
  -> ChromaDB persistent vector store
  -> hybrid retrieval ve metadata filtreleme
  -> safety guard
  -> Foundry Local LLM
  -> Streamlit sohbet arayuzu
```

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Foundry Local tarafinda OpenAI uyumlu endpoint varsayilan olarak `http://127.0.0.1:54312/v1` adresinde beklenir. Degistirmek icin `.env` dosyasi olusturabilirsiniz:

```env
FOUNDRY_BASE_URL=http://127.0.0.1:54312/v1
FOUNDRY_API_KEY=test
FOUNDRY_MODEL=Phi-3.5-mini-instruct-generic-gpu:2
```

## Calistirma

Once demo belgelerini indeksleyin:

```bash
python ingest.py
```

Sonra arayuzu acin:

```bash
streamlit run app.py
```

## Onemli Sinirlar

- Bu uygulama teshis koymaz, tedavi onermez, doz degisikligi tavsiye etmez.
- Yanitlar yalnizca yuklenen belgelerdeki metne dayanir.
- Demo belgeleri egitim amaclidir. Gercek kullanim icin resmi ve guncel kaynaklardan alinan KUB/KT dokumanlari eklenmelidir.
- Saglikla ilgili kararlar icin doktor veya eczaciya basvurulmalidir.

## Dosya Yapisi

```text
app.py
ingest.py
rag/
  config.py
  document_loader.py
  chunker.py
  vector_store.py
  retriever.py
  safety.py
  generator.py
  prompts.py
docs/
  demo_*.txt
data/
  chroma/
eval_questions.json
```
