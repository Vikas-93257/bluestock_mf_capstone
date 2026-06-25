# Bluestock Fintech – Mutual Fund Analytics Capstone

**Intern:** Vikas – Data Analyst Intern  
**Company:** Bluestock Fintech Pvt. Ltd., Pune  
**Project:** Capstone Project I – Mutual Fund Analytics  
**Start Date:** 20 Jun 2026

## Day 1 – Project Setup + Data Ingestion (ETL)
**Completed:** 25 Jun 2026

### Deliverables
- `scripts/data_ingestion.py`
- `scripts/live_nav_fetch.py`
- `requirements.txt`
- GitHub repo – Day 1 commit

### Datasets loaded (10)
- `01_fund_master.csv` – 40 rows
- `02_nav_history.csv` – 46000 rows
- `03_aum_by_fund_house.csv` – 90 rows
- `04_monthly_sip_inflows.csv` – 48 rows – **12 NULLs in yoy_growth_pct**
- `05_category_inflows.csv` – 144 rows
- `06_industry_folio_count.csv` – 21 rows
- `07_scheme_performance.csv` – 40 rows
- `08_investor_transactions.csv` – 32778 rows
- `09_portfolio_holdings.csv` – 322 rows
- `10_benchmark_indices.csv` – 8050 rows

### Live NAV – 25 Jun 2026
- 125497 HDFC_TOP_100 → SBI Small Cap Direct – 205.0655 – 24-06-2026
- 119551 SBI_Bluechip → Aditya Birla Banking & PSU Debt – 106.1268
- 120503 ICICI_Bluechip → Axis ELSS Tax Saver – 108.2944
- 118632 Nippon_Large_Cap → Nippon India Large Cap ✅ – 101.0387
- 119092 Axis_Bluechip → HDFC Money Market – 6204.477
- 120841 Kotak_Bluechip → quant Mid Cap – 249.8412

**Finding:** mfapi.in scheme_code mismatch – 5/6 codes differ from fund_master. Documented.

### AMFI Validation
- fund_master: 40 codes
- nav_history: 40 codes
- **Match: 100% – 0 missing, 0 orphan**
- scheme_performance: 40/40
- investor_transactions: 40/40
- portfolio_holdings: 34/40

### Fund Master Insights
- Fund Houses (10): SBI, HDFC, ICICI Prudential, Nippon India, Kotak Mahindra, Axis, Aditya Birla Sun Life, UTI, Mirae Asset, DSP
- Categories: Equity, Debt
- Sub-Categories (12): Large Cap, Small Cap, Mid Cap, Flexi Cap, Large & Mid Cap, ELSS, Value, Index, Index/ETF, Gilt, Short Duration, Liquid
- Risk: Moderate, Very High, Low, High, Moderately High
- Plan: Regular 32, Direct 8

### How to run
```bash
pip install -r requirements.txt
python scripts/data_ingestion.py
python scripts/live_nav_fetch.py