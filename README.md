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

## Demo Akisi

1. `python ingest.py` ile `docs/` klasorundeki belgeleri ChromaDB'ye indeksleyin.
2. `streamlit run app.py` ile arayuzu acin.
3. Ilac filtresini "Tum belgeler" veya belirli bir demo belge olarak secin.
4. Ornek sorular sorun:

```text
Demo Antihistaminik hangi alerji belirtileri icin ornek bilgi iceriyor?
Demo Analjezik belgesinde ciddi alerji belirtisi olarak neler geciyor?
Demo Antiasit belgesinde saklama kosullari nasil anlatiliyor?
Bu ilaci kullanayim mi?
Yanlislikla cok fazla ictim ve nefes almakta zorlaniyorum, ne yapayim?
```

5. Cevabin altindaki "Kullanilan kaynak parcalari" bolumunden kaynaklari kontrol edin.

## Bilesenler

- `rag/document_loader.py`: PDF, TXT ve Markdown belgelerini okur.
- `rag/chunker.py`: Metni bolum farkindalikli parcalara ayirir.
- `rag/vector_store.py`: Embedding modeli ve ChromaDB persistent store katmanini yonetir.
- `rag/retriever.py`: Semantic search, ilac filtresi ve bolum bazli skor artirimi yapar.
- `rag/safety.py`: Acil durum, doz degisikligi ve kisisel tibbi karar sorularini yakalar.
- `rag/generator.py`: Foundry Local OpenAI uyumlu endpoint uzerinden cevap uretir.
- `app.py`: Streamlit sohbet arayuzu.
- `ingest.py`: Belgeleri indeksleme komutu.
- `evaluate.py`: Test sorulari icin retrieval ve safety smoke report.

## Degerlendirme

Indeksleme yapildiktan sonra:

```bash
python evaluate.py
```

Bu komut, `eval_questions.json` icindeki sorular icin safety kararini ve en iyi kaynak
parcasini raporlar. Tam otomatik dogruluk olcumu degildir; demo oncesi hizli kalite
kontrolu icindir.

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
