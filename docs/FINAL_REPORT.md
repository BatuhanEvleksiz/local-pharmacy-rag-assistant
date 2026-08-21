# Final Raporu

## Proje Ozeti

Yerel Eczacılık RAG Asistanı, eczacılık alanında resmi belgeye dayalı soru-cevap deneyimi sunan lokal bir RAG projesidir. Sistem TİTCK resmi listelerini ve seçili ilaçların KÜB/KT PDF'lerini yerelde indeksler, kullanıcı sorusuna en ilgili kaynak parçalarını bulur ve Foundry Local açıksa kaynaklı cevap üretir.

## Problem

İlaç bilgisi sorularında güvenilir kaynak, izlenebilirlik ve güvenlik kritik önemdedir. Genel LLM cevapları yan etki, doz veya kullanım gibi konularda uydurma bilgi üretebilir. Bu proje, cevapları yerel resmi belgelere bağlayarak bu riski azaltmayı hedefler.

## Cozum

- Resmi TİTCK listeleri otomatik indirilir ve metin korpusuna donusturulur.
- Urun bazli KUB/KT PDF'leri indirilebilir.
- Belgeler bolum farkindalikli chunk'lara ayrilir.
- `intfloat/multilingual-e5-small` embedding modeli ile ChromaDB'ye kaydedilir.
- Retrieval katmanı ilaç adı, sorgu terimi ve bölüm ipuçlarıyla skorlamayı iyileştirir.
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
- Seed listedeki yaygın ilaçlar için KÜB/KT indirme desteği eklendi.
- Yerelde 44 belge ve 4767 chunk indekslendi.
- `evaluate.py` gercek korpus sorulariyla smoke test uretiyor.
- Streamlit arayuzunde veri indirme ve yeniden indeksleme paneli var.

## Sinirlar

- Tüm ilaçların tüm KÜB/KT PDF'leri otomatik indirilmiş değil; seed liste ile başlandı.
- Foundry Local modeli calismiyorsa uretken cevap yerine kaynak parcasi fallback'i gosterilir.
- Bu sistem karar destek veya teshis sistemi degildir; yalnizca belge ozeti ve kaynakli bilgi verir.

## Sonraki Iyilestirmeler

- KUB/KT PDF kapsam sayisini sistematik olarak artirmak.
- Retrieval icin reranker eklemek.
- Evaluation sonucunu otomatik pass/fail metriklerine donusturmek.
- Kaynaklarda sayfa numarasi ve PDF linki gostermek.
- Foundry Local model saglik kontrolunu arayuzde ayri bir durum metriği olarak gostermek.
