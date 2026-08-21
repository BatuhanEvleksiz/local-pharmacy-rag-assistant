# Proje Tamamlama Plani

Bu belge, Yerel Eczacılık RAG Asistanı'nın staj demosu için tamamlanması gereken teknik kapsamı ve kabul kriterlerini listeler.

## Kabul Kriterleri

- Resmi TİTCK ilaç listeleri yerel korpusa dönüştürülebilmeli.
- Seçili yaygın ilaçlar için KÜB/KT PDF'leri indirilebilmeli.
- KUB/KT metinleri yan etki, kullanim, saklama ve uyarilar gibi klinik bilgi sorularinda kaynak olarak donebilmeli.
- Sistem, sadece liste kaydi olan durumlarda yan etki/doz gibi klinik detaylari uydurmadan reddedebilmeli.
- Foundry Local kapaliyken uygulama hata vermeden kaynak parcasi ozeti gosterebilmeli.
- Foundry Local acikken cevaplar kaynaklara dayali ve Turkce uretilmeli.
- Streamlit arayuzunde indeks durumu, kaynak goruntuleme ve guvenlik uyarilari net olmalı.
- Demo icin gercekci test sorulari ve kisa bir sunum akisi bulunmali.

## Adimlar

1. Dokumantasyon ve bitis kriterlerini netlestir.
2. KÜB/KT indiriciyi çoklu ilaç listesiyle çalışacak hale getir.
3. Yaygın ilaçlardan oluşan seed listesini ekle.
4. Gercek veri odakli degerlendirme sorularini guncelle.
5. Streamlit'e KUB/KT indirme ve yeniden indeksleme akisina yardimci panel ekle.
6. Foundry Local ile uctan uca demo testi yap.
7. Final raporu, mimari diyagram ve demo senaryosunu ekle.
