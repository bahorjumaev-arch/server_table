# cluster_pipeline

Cluster monitoring data'sidan noldan **data pipeline** qurish: raw data → profiling → cleaning → database → handoff.

Bu project startup'dagi rolingni imitatsiya qiladi: data collection, data cleaning va backend developer uchun tayyor database tayyorlash.

## Senariy

Sening "kompaniyang" 120 ta server'li, 4 ta cluster'ni (alpha, beta, gamma, delta) boshqaradi. Backend developer dashboard va alerting qurmoqchi, lekin unga toza, ishonchli database kerak. Data uch xil source'dan keladi va hech biri toza emas.

## Raw data (data/raw/)

| Fayl | Nima | Hajmi |
|---|---|---|
| `servers_inventory.csv` | server ro'yxati (spreadsheet'dan export) | ~126 row |
| `metrics_2026-10-01.jsonl` ... `metrics_2026-10-07.jsonl` | har 15 daqiqada server metrikalari, kuniga bitta fayl | ~80 000 line |
| `cluster_events.log` | turli service'lardan matn ko'rinishidagi log | ~5 100 line |

## Boshlash

```bash
python generate_raw_data.py
```

Script `data/raw/` ichiga fayllarni yozadi. Seed qat'iy, shuning uchun har safar bir xil data chiqadi.

## Qoidalar

1. `generate_raw_data.py` fayliga tegma.
2. `data/raw/` ichidagi fayllarni qo'lda tahrirlama. Raw data o'zgarmas bo'lishi kerak.
3. Hamma narsa script bilan qilinsin (Excel'da qo'lda to'g'rilash yo'q), qayta ishga tushirsang bir xil natija chiqsin.
4. Har bosqichdan keyin Git commit qil.
5. Muammolarni o'zing topasan. Qaysi defect bor, nechta, qayerda: buni profiling bosqichida aniqlaysan.

## Papka tuzilmasi

```
cluster_pipeline/
├── data/
│   ├── raw/        # o'zgarmaydi
│   ├── staging/    # ingestion natijasi
│   └── clean/      # cleaning natijasi
├── src/            # sening Python kodlaring
├── sql/            # schema, quality checks, sample queries
├── docs/           # hujjatlar
├── generate_raw_data.py
└── README.md
```

## Bosqichlar

Har bosqichda faqat **vazifa** va **tayyor bo'lish mezoni** (Done) yozilgan.

### Stage 1. Source inventory

**Vazifa:** Uch source'ni ham ochib ko'r va ularni tavsiflab ber.

**Done:** `docs/source_inventory.md` da har source uchun: format, column'lar/field'lar, hajm, vaqt oralig'i, birinchi qarashda ko'ringan g'alati narsalar.

### Stage 2. Ingestion (collection)

**Vazifa:** `src/ingest.py` yoz: uch source'ni o'qib, staging'ga yozsin.

**Done:**
- bitta buzuq line butun jarayonni to'xtatmaydi
- nechta line o'qildi / nechtasi o'qilmadi, log'ga yoziladi
- har row'da qaysi fayldan kelgani saqlanadi
- raw fayllar o'zgarmaydi

### Stage 3. Profiling

**Vazifa:** `src/profile.py` yoz: har source uchun data quality report chiqarsin.

**Done:** `docs/data_quality_report.md` da har source bo'yicha topilgan muammolar turi va soni. Report script orqali hosil bo'lsin.

### Stage 4. Cleaning

**Vazifa:** `src/clean.py` yoz: staging'dan clean data hosil qilsin.

**Done:**
- `docs/cleaning_rules.md` da har bir qoida va uning sababi yozilgan (nimani o'chirding, nimani to'g'rilading, nimani o'zgartirmading va nega)
- o'chirilgan yoki rad etilgan row'lar sabab bilan alohida saqlanadi
- script ikkinchi marta ishga tushsa bir xil natija beradi

### Stage 5. Database design

**Vazifa:** Clean data uchun schema loyihala.

**Done:**
- `sql/schema.sql`: table'lar, primary key, foreign key, `CHECK` constraint'lar, index'lar
- `docs/er_diagram.png` (qo'lda chizilsa ham bo'ladi)
- boshlash uchun SQLite, keyin xohlasang SQL Server (T-SQL) ga ko'chir

### Stage 6. Loading

**Vazifa:** `src/load.py` yoz: clean data'ni database'ga yuklasin.

**Done:** script ketma-ket ikki marta ishga tushganda duplicate paydo bo'lmaydi (idempotent).

### Stage 7. Data quality checks

**Vazifa:** Database yuklangandan keyin avtomatik tekshiruvlar yoz.

**Done:** `sql/quality_checks.sql` yoki `src/checks.py` da kamida 8 ta check, har biri PASS/FAIL natija beradi.

### Stage 8. Handoff

**Vazifa:** Backend developer shu database'dan foydalana olishi uchun hujjat tayyorla.

**Done:**
- `docs/data_dictionary.md`: har table va column ma'nosi, type'i, mumkin bo'lgan qiymatlari
- `sql/sample_queries.sql`: kamida 5 ta biznes savoliga javob beradigan query, masalan:
  - eng ko'p `ERROR` va `CRITICAL` bergan 10 ta server
  - har cluster'ning kunlik o'rtacha CPU'si
  - disk 90% dan oshgan server'lar
  - metrics'i eng ko'p yetishmagan server'lar
  - inventory'da bor, lekin metrics yubormagan server'lar

## Bonus

- Pipeline'ni bitta `run_pipeline.py` bilan ketma-ket ishga tushirish
- `cron` yoki Airflow bilan schedule qilish
- Power BI dashboard (cluster health)
- Unit test'lar (cleaning funksiyalari uchun `pytest`)

## Yordam so'rash

Qotib qolsang, aniq qaysi bosqichda ekaningni, nima kutganingni va nima chiqayotganini yoz. Yechim faqat so'raganingda beriladi.
