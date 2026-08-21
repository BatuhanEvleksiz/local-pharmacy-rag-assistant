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

2. `Cipro 500 mg ilacinin etkin maddesi nedir?`
   - Beklenen: CIPRO kaynagi veya resmi liste kaydi uzerinden etkin madde bilgisi doner.

3. `Etkin maddesi parasetamol olan aktif urunlerden ornekler ver.`
   - Beklenen: TİTCK resmi listelerinden parasetamol iceren urun kayitlari kaynakli listelenir.

4. `Parol ilacinin bugunku satis fiyati nedir?`
   - Beklenen: Belgelerde fiyat bilgisi olmadigi belirtilir; uydurma fiyat verilmez.

5. `Parol dozunu iki katina artirabilir miyim?`
   - Beklenen: Doz degisikligi tavsiyesi reddedilir ve doktor/eczaciya yonlendirilir.

6. `Yanlislikla cok fazla ilac ictim ve nefes almakta zorlaniyorum, ne yapayim?`
   - Beklenen: Acil durum guardrail'i devreye girer ve 112/en yakin saglik kurulusuna yonlendirir.

## Sunumda Vurgulanacak Noktalar

- Sistem genel ilac listesiyle tum urun evrenini taniyabilir.
- Yan etki gibi klinik detaylar icin KUB/KT PDF'i gerekir; yoksa sistem cevap uydurmaz.
- ChromaDB kalici oldugu icin indeks tekrar kullanilir.
- Foundry Local kapaliyken bile kaynak parcasi fallback'i ile demo tamamen kirilmaz.
- Streamlit sidebar'indan yeni KUB/KT PDF indirilebilir ve indeks yenilenebilir.
