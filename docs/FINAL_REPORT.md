# Final Raporu

## Proje Ozeti

Yerel Eczacilik RAG Asistani, eczacilik alaninda resmi belgeye dayali soru-cevap deneyimi sunan lokal bir RAG projesidir. Sistem TİTCK resmi listelerini ve secili ilaclarin KUB/KT PDF'lerini yerelde indeksler, kullanici sorusuna en ilgili kaynak parcalarini bulur ve Foundry Local aciksa kaynakli cevap uretir.

## Problem

Ilac bilgisi sorularinda guvenilir kaynak, izlenebilirlik ve guvenlik kritik onemdedir. Genel LLM cevaplari yan etki, doz veya kullanim gibi konularda uydurma bilgi uretebilir. Bu proje, cevaplari yerel resmi belgelere baglayarak bu riski azaltmayi hedefler.

## Cozum

- Resmi TİTCK listeleri otomatik indirilir ve metin korpusuna donusturulur.
- Urun bazli KUB/KT PDF'leri indirilebilir.
- Belgeler bolum farkindalikli chunk'lara ayrilir.
- `intfloat/multilingual-e5-small` embedding modeli ile ChromaDB'ye kaydedilir.
- Retrieval katmani ilac adi, sorgu terimi ve bolum ipuclariyla skorlamayi iyilestirir.
- Safety guardrail doz, kisisel tedavi ve acil durum sorularini cevap uretiminden once yakalar.
- Foundry Local ulasilamazsa kullaniciya kaynak parcasi ozeti verilir.

## Kullanilan Teknolojiler

- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- Microsoft Foundry Local uyumlu OpenAI endpoint
- TİTCK resmi veri kaynaklari
- pdfplumber / pypdf

## Mevcut Durum

- GitHub repo public olarak olusturuldu ve adim adim commit'lendi.
- Resmi liste modu calisiyor.
- Seed listedeki yaygin ilaclar icin KUB/KT indirme destegi eklendi.
- Yerelde 44 belge ve 4767 chunk indekslendi.
- `evaluate.py` gercek korpus sorulariyla smoke test uretiyor.
- Streamlit arayuzunde veri indirme ve yeniden indeksleme paneli var.

## Sinirlar

- Tum ilaclarin tum KUB/KT PDF'leri otomatik indirilmis degil; seed liste ile baslandi.
- Foundry Local modeli calismiyorsa uretken cevap yerine kaynak parcasi fallback'i gosterilir.
- Bu sistem karar destek veya teshis sistemi degildir; yalnizca belge ozeti ve kaynakli bilgi verir.

## Sonraki Iyilestirmeler

- KUB/KT PDF kapsam sayisini sistematik olarak artirmak.
- Retrieval icin reranker eklemek.
- Evaluation sonucunu otomatik pass/fail metriklerine donusturmek.
- Kaynaklarda sayfa numarasi ve PDF linki gostermek.
- Foundry Local model saglik kontrolunu arayuzde ayri bir durum metriği olarak gostermek.
