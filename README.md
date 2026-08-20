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

Once resmi veri belgelerini olusturun:

```bash
python scripts/fetch_titck_data.py
```

Sonra belgeleri indeksleyin:

```bash
python ingest.py
```

Sonra arayuzu acin:

```bash
streamlit run app.py
```

## Demo Akisi

1. `python scripts/fetch_titck_data.py` ile TİTCK resmi listelerinden yerel korpus uretin.
2. `python ingest.py` ile `real_docs/` klasorundeki belgeleri ChromaDB'ye indeksleyin.
3. `streamlit run app.py` ile arayuzu acin.
4. Ilac filtresini "Tum belgeler" veya belirli bir ilac kaydi olarak secin.
5. Ornek sorular sorun:

```text
PAROL hakkinda hangi bilgiler var?
Etkin maddesi parasetamol olan urunleri ozetle.
Ruhsat sahibi firma bilgisi nedir?
Bu ilaci kullanayim mi?
Yanlislikla cok fazla ictim ve nefes almakta zorlaniyorum, ne yapayim?
```

6. Cevabin altindaki "Kullanilan kaynak parcalari" bolumunden kaynaklari kontrol edin.

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
- `scripts/fetch_titck_data.py`: TİTCK resmi XLSX listelerini indirir ve `real_docs/` icin metin korpusu uretir.

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
- Varsayilan mod TİTCK resmi listelerinden uretilen yerel korpusla calisir.
- KUB/KT PDF metinleri eklenirse sistem ayni `real_docs/` klasorunden indeksleyebilir.
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
examples/demo_docs/
  demo_*.txt
real_docs/
  titck_*.txt
data_sources/
  titck_*.xlsx
data/
  chroma/
eval_questions.json
```
