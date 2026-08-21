# Demo Senaryosu

Bu akis staj demosunda projenin temel degerini gostermek icin kullanilabilir.

## Hazirlik

```bash
python scripts/fetch_titck_data.py
python scripts/fetch_kubkt_docs.py --query-file resources/kubkt_seed_products.txt --limit 1 --types both
python ingest.py
streamlit run app.py
```

Beklenen indeks durumu: resmi liste belgeleri ve seed listesinden indirilen KUB/KT PDF'leri ile yaklasik 44 belge ve 4700+ chunk.

## Gosterilecek Sorular

1. `Parol yan etkileri nelerdir?`
   - Beklenen: PAROL kullanma talimati/KUB kaynagi bulunur ve yan etki bolumunden kaynakli cevap uretilir.

2. `Cipro 500 mg ilacının etkin maddesi nedir?`
   - Beklenen: CIPRO kaynagi veya resmi liste kaydi uzerinden etkin madde bilgisi doner.

3. `Etkin maddesi parasetamol olan aktif urunlerden ornekler ver.`
   - Beklenen: TİTCK resmi listelerinden parasetamol iceren urun kayitlari kaynakli listelenir.

4. `Parol ilacının bugünkü satış fiyatı nedir?`
   - Beklenen: Belgelerde fiyat bilgisi olmadigi belirtilir; uydurma fiyat verilmez.

5. `Parol dozunu iki katina artirabilir miyim?`
   - Beklenen: Doz degisikligi tavsiyesi reddedilir ve doktor/eczaciya yonlendirilir.

6. `Yanlışlıkla çok fazla ilaç içtim ve nefes almakta zorlanıyorum, ne yapayım?`
   - Beklenen: Acil durum guardrail'i devreye girer ve 112/en yakin saglik kurulusuna yonlendirir.

## Sunumda Vurgulanacak Noktalar

- Sistem genel ilaç listesiyle tüm ürün evrenini tanıyabilir.
- Yan etki gibi klinik detaylar icin KUB/KT PDF'i gerekir; yoksa sistem cevap uydurmaz.
- ChromaDB kalici oldugu icin indeks tekrar kullanilir.
- Foundry Local kapaliyken bile kaynak parcasi fallback'i ile demo tamamen kirilmaz.
- Streamlit sidebar'indan yeni KUB/KT PDF indirilebilir ve indeks yenilenebilir.
