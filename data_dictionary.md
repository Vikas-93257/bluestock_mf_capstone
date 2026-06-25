# Bluestock MF – Data Dictionary
## Capstone Project I – Mutual Fund Analytics

**Author:** Vikas Maurya  
**Company:** Bluestock Fintech Pvt. Ltd., Pune  
**Date:** 26 Jun 2026  
**Version:** Day 2 – v1.0  
**Database:** `bluestock_mf.db` – SQLite – Star Schema

---

## 1. Overview

| Layer | Tables | Purpose |
|---|---|---|
| Dimension | `dim_fund`, `dim_date` | Master / lookup – slow changing |
| Fact | `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `fact_portfolio` | Measurable events – fast growing |

**Total tables:** 6 core + 1 date dim = 7  
**Total columns:** ~65  
**Total rows:** ~97,278  
**Database size:** 5.2 MB (`bluestock_mf.db`)

---

## 2. dim_fund – Fund Master Dimension

**Primary Key:** `amfi_code` (INTEGER)  
**Rows:** 40  
**Source:** `01_fund_master.csv` → `clean_fund_master.csv`  
**Grain:** 1 row = 1 mutual fund scheme  
**Type:** SCD Type 1 – Slowly Changing Dimension

| column | SQL type | Python dtype | Nullable | Business Definition | Example | Source |
|---|---|---|---|---|---|---|
| amfi_code | INTEGER PK | int64 | NO | AMFI unique scheme code – Bluestock internal – 6 digit | 119551 | 01_fund_master.csv |
| fund_house | TEXT NOT NULL | object | NO | Asset Management Company name | SBI Mutual Fund | fund_master.fund_house |
| scheme_name | TEXT NOT NULL | object | NO | Full official AMFI scheme name | SBI Bluechip Fund - Regular Plan - Growth | fund_master.scheme_name |
| category | TEXT | object | YES | SEBI broad category | Equity / Debt | fund_master.category |
| sub_category | TEXT | object | YES | SEBI sub-category – 12 values | Large Cap, Small Cap, Mid Cap, Flexi Cap, ELSS, Gilt, Liquid, Short Duration, Value, Index, Index/ETF, Large & Mid Cap | fund_master.sub_category |
| plan | TEXT CHECK (Regular/Direct) | object | YES | Direct = lower expense, no distributor commission / Regular = distributor commission included | Direct | fund_master.plan |
| launch_date | DATE | object → datetime | YES | Fund launch – YYYY-MM-DD | 2006-02-14 | fund_master.launch_date |
| benchmark | TEXT | object | YES | Official benchmark index | NIFTY 100 TRI | fund_master.benchmark |
| expense_ratio_pct | REAL | float64 | YES | Annual TER % – SEBI cap 0.1 – 2.5% validated Day 2 | 1.54 | fund_master.expense_ratio_pct |
| exit_load_pct | REAL | float64 | YES | Exit load if redeemed early % | 1.0 | fund_master.exit_load_pct |
| min_sip_amount | INTEGER | int64 | YES | Minimum SIP Rs. | 500 | fund_master.min_sip_amount |
| min_lumpsum_amount | INTEGER | int64 | YES | Minimum lumpsum Rs. | 1000 | fund_master.min_lumpsum_amount |
| fund_manager | TEXT | object | YES | Primary fund manager | Sohini Andani | fund_master.fund_manager |
| risk_category | TEXT | object | YES | SEBI Risk-o-meter | Low / Moderate / Moderately High / High / Very High | fund_master.risk_category |
| sebi_category_code | TEXT | object | YES | Internal – EC01=LargeCap, EC02=MidCap, EC03=SmallCap, DC01=Liquid, DC02=Gilt | EC01 | fund_master.sebi_category_code |

**Business rules:**
- `amfi_code` UNIQUE – PK enforced
- `plan` ∈ {Regular, Direct}
- `category` ∈ {Equity, Debt}
- `expense_ratio_pct` BETWEEN 0.1 AND 2.5 – validated Day 2 Task 3

---

## 3. fact_nav – Daily NAV Fact

**Primary Key:** `(amfi_code, nav_date)` – composite  
**Foreign Key:** `amfi_code → dim_fund(amfi_code)`  
**Rows:** 64,320 (46,000 raw + 18,320 holiday ffill – Day 2 Task 1)  
**Source:** `02_nav_history.csv` → `clean_nav_history.csv`  
**Grain:** 1 row = 1 scheme × 1 calendar day  
**Update frequency:** Daily

| column | SQL type | Python dtype | Nullable | Business Definition | Example | Source / Transform |
|---|---|---|---|---|---|---|
| amfi_code | INTEGER FK NOT NULL | int64 | NO | → dim_fund.amfi_code | 119551 | nav_history.amfi_code |
| nav_date | DATE NOT NULL | datetime64 → str YYYY-MM-DD | NO | Trading / calendar date – forward-filled | 2022-01-03 | nav_history.date → parse_dates → ffill |
| nav | REAL NOT NULL CHECK >0 | float64 | NO | Net Asset Value Rs. per unit – validated >0 | 54.3856 | nav_history.nav |

**Transformations – Day 2 Task 1:**
1. `parse_dates=['date']` → datetime
2. `sort_values(['amfi_code','date'])`
3. `drop_duplicates()` → 0 removed
4. `nav > 0` filter → 0 removed
5. **Forward-fill:** reindex per amfi_code → `pd.date_range(..., freq='D')` → `ffill()` → weekends/holidays filled
6. Result: 46,000 → 64,320 rows (+18,320)

**Business rules:**
- PK `(amfi_code, nav_date)` UNIQUE
- `nav > 0` CHECK enforced
- FK → dim_fund

---

## 4. fact_transactions – Investor Transaction Fact

**Primary Key:** `tx_id INTEGER PRIMARY KEY AUTOINCREMENT`  
**Foreign Key:** `amfi_code → dim_fund(amfi_code)`  
**Rows:** 32,778  
**Source:** `08_investor_transactions.csv` → `clean_transaction.csv`  
**Grain:** 1 row = 1 investor transaction  
**Update frequency:** Daily (simulated)

| column | SQL type | Python dtype | Nullable | Business Definition | Example | Source / Transform |
|---|---|---|---|---|---|---|
| tx_id | INTEGER PK AUTOINCREMENT | – | NO | Surrogate transaction ID | 1 | auto |
| investor_id | TEXT | object | YES | Anonymized – INV000001 … INV005000 | INV003054 | investor_transactions.investor_id |
| transaction_date | DATE | object → datetime → str | YES | YYYY-MM-DD – validated | 2024-01-01 | transaction_date → pd.to_datetime |
| amfi_code | INTEGER FK | int64 | YES | → dim_fund | 119092 | investor_transactions.amfi_code |
| transaction_type | TEXT CHECK | object | YES | ENUM: SIP / Lumpsum / Redemption | SIP | transaction_type → .str.lower().map() → standardised Day 2 Task 2 |
| amount_inr | INTEGER CHECK >0 | int64 | YES | Transaction amount Rs. – validated >0 | 1834 | amount_inr – validated >0 |
| state | TEXT | object | YES | Indian state | Telangana | state |
| city | TEXT | object | YES | | Hyderabad | city |
| city_tier | TEXT | object | YES | T30 (Top 30) / B30 (Beyond 30) – AMFI geo classification | T30 | city_tier |
| age_group | TEXT | object | YES | 18-25 / 26-35 / 36-45 / 46-55 / 56+ | 56+ | age_group |
| gender | TEXT | object | YES | Male / Female | Female | gender |
| annual_income_lakh | REAL | float64 | YES | Annual income Rs. lakh | 77.1 | annual_income_lakh |
| payment_mode | TEXT | object | YES | UPI / Mandate / NetBanking / Cheque | UPI | payment_mode |
| kyc_status | TEXT CHECK | object | YES | ENUM: Verified / Pending | Verified | kyc_status – enum checked Day 2 Task 2 |

**Cleaning – Day 2 Task 2:**
- `transaction_type` standardised: sip→SIP, lumpsum→Lumpsum, redemption→Redemption
- `amount_inr > 0` validated → 0 bad found
- `transaction_date` → `pd.to_datetime` → `YYYY-MM-DD` → 0 bad dates
- `kyc_status` enum: **Verified 30,146 / Pending 2,632** – both valid
- Duplicates: 0

**Business rules:**
- `transaction_type IN ('SIP','Lumpsum','Redemption')` – CHECK
- `amount_inr > 0` – CHECK
- `kyc_status IN ('Verified','Pending')` – validated

---

## 5. fact_performance – Scheme Performance Fact

**Primary Key:** `amfi_code`  
**Foreign Key:** `amfi_code → dim_fund(amfi_code)`  
**Rows:** 40 (1 per scheme)  
**Source:** `07_scheme_performance.csv` → `clean_performance.csv`  
**Grain:** 1 row = 1 scheme – latest snapshot  
**Update frequency:** Monthly

| column | SQL type | Python dtype | Business Definition | Formula / Source | Valid Range |
|---|---|---|---|---|---|
| amfi_code | INTEGER PK FK | int64 | → dim_fund | scheme_performance.amfi_code | 100016 – 149324 |
| return_1yr_pct | REAL | float64 | 1-year absolute return % | computed from NAV | -100 to +100 |
| return_3yr_pct | REAL | float64 | 3-year CAGR % | CAGR = (NAV_end/NAV_start)^(1/3)-1 | -50 to +50 |
| return_5yr_pct | REAL | float64 | 5-year CAGR % | CAGR 5yr | -50 to +50 |
| benchmark_3yr_pct | REAL | float64 | Benchmark 3yr CAGR for alpha calc | benchmark_indices join | – |
| alpha | REAL | float64 | Excess return vs benchmark | return_3yr_pct – benchmark_3yr_pct | -10 to +10 |
| beta | REAL | float64 | Market sensitivity – 1.0 = market | Cov(Rp,Rm)/Var(Rm) – scipy.linregress | 0.5 – 1.5 |
| sharpe_ratio | REAL | float64 | Risk-adjusted return | (Rp – Rf) / σp – Rf=6.5% | -2 to +3 – flagged <0 Day 2 |
| sortino_ratio | REAL | float64 | Downside risk-adjusted | (Rp – Rf) / downside_σ | -2 to +3 |
| std_dev_ann_pct | REAL | float64 | Annualised volatility % | σ_daily × √252 | 5 – 35 |
| max_drawdown_pct | REAL | float64 | Worst peak-to-trough % – negative | min(NAV/running_max – 1) | -50 to 0 |
| aum_crore | INTEGER | int64 | Scheme AUM Rs. crore | – | 100 – 50000 |
| expense_ratio_pct | REAL CHECK 0.1-2.5 | float64 | Annual TER % | – | **0.1 – 2.5 – SEBI validated** |
| morningstar_rating | INTEGER CHECK 1-5 | int64 | 1-5 stars | – | 1 – 5 |

**Cleaning – Day 2 Task 3:**
- All 13 numeric columns → `pd.to_numeric(..., errors='coerce')` → **0 nulls**
- Negative Sharpe flagged: **0**
- Alpha < -2 flagged: **0**
- Beta > 1.5 flagged: **0**
- expense_ratio 0.1-2.5% out of range: **0 ✅**
- morningstar_rating 1-5 out of range: **0**

---

## 6. fact_aum – Fund House AUM Fact

**Primary Key:** `(fund_house, aum_date)` – composite  
**Rows:** 90  
**Source:** `03_aum_by_fund_house.csv` → `clean_aum.csv`  
**Grain:** 1 row = 1 fund house × 1 quarter  
**Update frequency:** Quarterly

| column | SQL type | Python dtype | Business Definition | Example |
|---|---|---|---|---|
| fund_house | TEXT PK | object | AMC name | SBI Mutual Fund |
| aum_date | DATE PK | object → datetime → str | Quarter end – YYYY-MM-DD | 2022-03-31 |
| aum_lakh_crore | REAL | float64 | AUM Rs. lakh crore | 6.05 |
| aum_crore | INTEGER | int64 | AUM Rs. crore | 605000 |
| num_schemes | INTEGER | int64 | Active schemes count | 186 |

---

## 7. Other cleaned reference tables

| table / CSV | rows | key columns | purpose |
|---|---|---|---|
| `clean_category_inflows.csv` | 144 | month, category, net_inflow_crore | Category flow heatmap – Day 3 EDA |
| `clean_folio_count.csv` | 21 | month, total_folios_crore, equity_folios_crore, … | Industry folio growth – Day 3 |
| `clean_sip_inflows.csv` | 48 | month, sip_inflow_crore, active_sip_accounts_crore, … | SIP trend – Day 3 – **yoy_growth_pct ffill Day 2** |
| `clean_portfolio.csv` | 322 | amfi_code, stock_symbol, weight_pct, sector | Holdings + HHI – Day 6 |
| `clean_benchmark.csv` | 8050 | date, index_name, close_value | Alpha/Beta – Day 4 |

---

## 8. Data Quality Summary – Day 2 Post-Cleaning

| dataset | source rows | cleaned rows | nulls before | nulls after | duplicates removed | notes |
|---|---|---|---|---|---|---|
| nav_history | 46000 | **64320** | 0 | 0 | 0 | +18,320 holiday ffill |
| investor_transactions | 32778 | 32778 | 0 | 0 | 0 | transaction_type standardized |
| scheme_performance | 40 | 40 | 0 | 0 | 0 | Sharpe 0 negative, expense 0.1-2.5% PASS |
| fund_master | 40 | 40 | 0 | 0 | 0 | – |
| aum_by_fund_house | 90 | 90 | 0 | 0 | 0 | – |
| monthly_sip_inflows | 48 | 48 | **12** | **0** | 0 | **yoy_growth_pct ffill – Day 1 anomaly fixed** |
| category_inflows | 144 | 144 | 0 | 0 | 0 | – |
| industry_folio_count | 21 | 21 | 0 | 0 | 0 | – |
| portfolio_holdings | 322 | 322 | 0 | 0 | 0 | – |
| benchmark_indices | 8050 | 8050 | 0 | 0 | 0 | – |
| **TOTAL** | **87,533** | **105,853** | **12** | **0** | **0** | **100% clean** |

**Database:** `data/db/bluestock_mf.db` – **5.2 MB**  
**Tables loaded:** `dim_fund (40)`, `fact_nav (64,320)`, `fact_transactions (32,778)`, `fact_performance (40)`, `fact_aum (90)`  
**Row count verification:** **5/5 PASS – 100% match source CSVs**

---

## 9. Data Lineage