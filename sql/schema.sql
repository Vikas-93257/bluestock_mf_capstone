-- =========================================================
-- Bluestock Fintech – Mutual Fund Analytics Capstone
-- Day 2 – Task 4 – SQLite Star Schema
-- Author: Vikas Maurya
-- Date: 26 Jun 2026
-- =========================================================

-- Drop old tables if re-running
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;

-- =========================================================
-- DIMENSION TABLES
-- =========================================================

-- dim_fund – Master fund information
-- PK: amfi_code
-- Source: 01_fund_master.csv → clean_fund_master.csv
CREATE TABLE dim_fund (
  amfi_code           INTEGER PRIMARY KEY,
  fund_house          TEXT NOT NULL,
  scheme_name         TEXT NOT NULL,
  category            TEXT,
  sub_category        TEXT,
  plan                TEXT CHECK (plan IN ('Regular','Direct')),
  benchmark           TEXT,
  expense_ratio_pct   REAL,
  exit_load_pct       REAL,
  min_sip_amount      INTEGER,
  min_lumpsum_amount  INTEGER,
  fund_manager        TEXT,
  risk_category       TEXT,
  sebi_category_code  TEXT,
  launch_date         DATE
);

-- dim_date – Date dimension for time intelligence
-- PK: date_id
-- Helps Power BI time slicers – Day 5
CREATE TABLE dim_date (
  date_id     INTEGER PRIMARY KEY,
  full_date   DATE UNIQUE NOT NULL,
  year        INTEGER,
  month       INTEGER,
  quarter     INTEGER,
  month_name  TEXT,
  is_weekday  INTEGER
);

-- =========================================================
-- FACT TABLES
-- =========================================================

-- fact_nav – Daily NAV movements
-- PK: (amfi_code, nav_date) – composite
-- FK: amfi_code → dim_fund
-- Rows: ~64,320 (after holiday ffill – Day 2 Task 1)
-- Source: 02_nav_history.csv → clean_nav_history.csv
CREATE TABLE fact_nav (
  amfi_code   INTEGER NOT NULL,
  nav_date    DATE NOT NULL,
  nav         REAL NOT NULL CHECK (nav > 0),
  PRIMARY KEY (amfi_code, nav_date),
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_transactions – Investor buy/sell data
-- PK: tx_id AUTOINCREMENT
-- FK: amfi_code → dim_fund
-- Rows: 32,778
-- Source: 08_investor_transactions.csv → clean_transaction.csv
CREATE TABLE fact_transactions (
  tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
  investor_id         TEXT,
  transaction_date    DATE,
  amfi_code           INTEGER,
  transaction_type    TEXT CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
  amount_inr          INTEGER CHECK (amount_inr > 0),
  state               TEXT,
  city                TEXT,
  city_tier           TEXT,
  age_group           TEXT,
  gender              TEXT,
  annual_income_lakh  REAL,
  payment_mode        TEXT,
  kyc_status          TEXT CHECK (kyc_status IN ('Verified','Pending')),
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_performance – Risk-return metrics
-- PK: amfi_code – 1 row per scheme
-- FK: amfi_code → dim_fund
-- Rows: 40
-- Source: 07_scheme_performance.csv → clean_performance.csv
CREATE TABLE fact_performance (
  amfi_code           INTEGER PRIMARY KEY,
  return_1yr_pct      REAL,
  return_3yr_pct      REAL,
  return_5yr_pct      REAL,
  benchmark_3yr_pct   REAL,
  alpha               REAL,
  beta                REAL,
  sharpe_ratio        REAL,
  sortino_ratio       REAL,
  std_dev_ann_pct     REAL,
  max_drawdown_pct    REAL,
  aum_crore           INTEGER,
  expense_ratio_pct   REAL CHECK (expense_ratio_pct BETWEEN 0.1 AND 2.5),
  morningstar_rating  INTEGER CHECK (morningstar_rating BETWEEN 1 AND 5),
  risk_grade          TEXT,
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_aum – Fund house AUM trends
-- PK: (fund_house, aum_date) – composite
-- Rows: 90 (quarterly 2022-2025 × 10 AMCs)
-- Source: 03_aum_by_fund_house.csv → clean_aum.csv
CREATE TABLE fact_aum (
  fund_house   TEXT NOT NULL,
  aum_date     DATE NOT NULL,
  aum_lakh_crore REAL,
  aum_crore    INTEGER,
  num_schemes  INTEGER,
  PRIMARY KEY (fund_house, aum_date)
);

-- =========================================================
-- INDEXES – fast BI queries – Day 5 Power BI
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_nav_code_date ON fact_nav(amfi_code, nav_date);
CREATE INDEX IF NOT EXISTS idx_tx_code_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_state ON fact_transactions(state);

-- =========================================================
-- END OF SCHEMA
-- Bluestock MF Capstone – Day 2 – Task 4 Complete
-- 6 tables: dim_fund, dim_date, fact_nav, fact_transactions, fact_performance, fact_aum
-- All PK + FK defined as per PDF
-- =========================================================