"""
Day 2 – Task 5 – Load cleaned data into SQLite
Bluestock Fintech – Mutual Fund Analytics Capstone
Author: Vikas Maurya
Date: 26 Jun 2026
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os

# --- paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_DIR = os.path.join(BASE_DIR, "data", "db")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")

print("="*70)
print("BLUESTOCK MF – DAY 2 – TASK 5")
print("Load cleaned data into SQLite")
print("="*70)
print(f"Database: {DB_PATH}")

# SQLAlchemy engine – Bluestock PDF requirement
# create_engine + df.to_sql()
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

print("\nConnecting to SQLite...")




# --- 1. dim_fund ---
# Source: clean_fund_master.csv
# PK: amfi_code
print("\n[1/5] Loading dim_fund ...")
df = pd.read_csv(os.path.join(PROC_DIR, "clean_fund_master.csv"))
print(f"  Source rows: {df.shape[0]}")

# Bluestock schema.sql ke columns se match karo
# dim_fund columns: amfi_code, fund_house, scheme_name, category, sub_category,
# plan, benchmark, expense_ratio_pct, exit_load_pct, min_sip_amount,
# min_lumpsum_amount, fund_manager, risk_category, sebi_category_code, launch_date
# → fund_master CSV me ye SAB columns already hain

df.to_sql("dim_fund", engine, if_exists="replace", index=False)
print(f"  ✓ Loaded into dim_fund")

# --- 2. fact_nav ---
# Source: clean_nav_history.csv
# PK: (amfi_code, nav_date)
print("\n[2/5] Loading fact_nav ...")
df = pd.read_csv(os.path.join(PROC_DIR, "clean_nav_history.csv"))
print(f"  Source rows: {df.shape[0]}")
# rename date → nav_date to match schema.sql
df = df.rename(columns={"date": "nav_date"})
df.to_sql("fact_nav", engine, if_exists="replace", index=False)
print(f"  ✓ Loaded into fact_nav")

# --- 3. fact_transactions ---
# Source: clean_transaction.csv
print("\n[3/5] Loading fact_transactions ...")
df = pd.read_csv(os.path.join(PROC_DIR, "clean_transaction.csv"))
print(f"  Source rows: {df.shape[0]}")
# rename transaction_date → already correct column name
# check column names match schema.sql:
# investor_id, transaction_date, amfi_code, transaction_type, amount_inr,
# state, city, city_tier, age_group, gender, annual_income_lakh, payment_mode, kyc_status
# → YES – clean_transaction.csv has all these – direct load
df.to_sql("fact_transactions", engine, if_exists="replace", index=False)
print(f"  ✓ Loaded into fact_transactions")

# --- 4. fact_performance ---
# Source: clean_performance.csv
print("\n[4/5] Loading fact_performance ...")
df = pd.read_csv(os.path.join(PROC_DIR, "clean_performance.csv"))
print(f"  Source rows: {df.shape[0]}")
# keep only columns defined in schema.sql fact_performance
perf_cols = [
    "amfi_code",
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "alpha", "beta",
    "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct", "morningstar_rating"
]
# check all cols exist
missing = [c for c in perf_cols if c not in df.columns]
if missing:
    print(f"  WARNING missing cols: {missing}")
df[perf_cols].to_sql("fact_performance", engine, if_exists="replace", index=False)
print(f"  ✓ Loaded into fact_performance")

# --- 5. fact_aum ---
# Source: clean_aum.csv
print("\n[5/5] Loading fact_aum ...")
df = pd.read_csv(os.path.join(PROC_DIR, "clean_aum.csv"))
print(f"  Source rows: {df.shape[0]}")
# rename date → aum_date to match schema.sql
if "date" in df.columns:
    df = df.rename(columns={"date": "aum_date"})
df.to_sql("fact_aum", engine, if_exists="replace", index=False)
print(f"  ✓ Loaded into fact_aum")




# =========================================================
# VERIFY – Row counts must match source CSVs – PDF Task 5
# =========================================================
print("\n" + "="*70)
print("VERIFYING ROW COUNTS – source CSV vs SQLite DB")
print("="*70)

# expected counts from Day 2 cleaning
expected = {
    "dim_fund": 40,
    "fact_nav": 64320,
    "fact_transactions": 32778,
    "fact_performance": 40,
    "fact_aum": 90
}

from sqlalchemy import text

all_ok = True
with engine.connect() as conn:
    for table, exp_count in expected.items():
        try:
            # count rows in DB
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            db_count = result.scalar()
            
            # check match
            status = "✓ PASS" if db_count == exp_count else "✗ FAIL"
            if db_count != exp_count:
                all_ok = False
            
            print(f"{table:20} | DB: {db_count:>6} | Expected: {exp_count:>6} | {status}")
        except Exception as e:
            print(f"{table:20} | ERROR: {e}")
            all_ok = False

print("="*70)
if all_ok:
    print("✓✓✓ ALL ROW COUNTS MATCH SOURCE CSVs ✅")
    print("✓✓✓ Day 2 – Task 5 – SQLite DB loaded successfully ✅")
else:
    print("✗✗✗ ROW COUNT MISMATCH – check ETL pipeline")

# Check database file size
import os
db_size_kb = os.path.getsize(DB_PATH) / 1024
print(f"\nDatabase file: {DB_PATH}")
print(f"Database size: {db_size_kb:.1f} KB")

# List all tables in DB
print("\nTables in bluestock_mf.db:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    tables = [row[0] for row in result]
    for t in tables:
        print(f"  - {t}")

print("\n" + "="*70)
print("NEXT: sql/queries.sql  →  10 analytical SQL queries")
print("="*70)