"""
Day 1 – Data Ingestion (ETL)
Bluestock Fintech – Mutual Fund Analytics Capstone
Date: 20 Jun 2026
Author: Vikas
Intern – Bluestock Fintech, Pune
"""

import pandas as pd
import os
import sys

# --- find project root automatically ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

print("="*80)
print("BLUESTOCK MUTUAL FUND ANALYTICS – DAY 1 DATA INGESTION")
print("Project: Capstone Project I - Mutual Fund Analytics")
print("Date: 20 Jun 2026")
print("="*80)

files = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv"
}

print("\nChecking data/raw folder...")
print("RAW_DIR =", RAW_DIR)
missing = []
for name, fname in files.items():
    fpath = os.path.join(RAW_DIR, fname)
    if not os.path.exists(fpath):
        print(f"  MISSING: {fname}")
        missing.append(fname)
    else:
        print(f"  FOUND: {fname}")

if missing:
    print("\nERROR: Missing files!")
    sys.exit(1)

print("\nAll 10 files found. Starting ingestion...\n")

dfs = {}
anomalies = []

for name, fname in files.items():
    path = os.path.join(RAW_DIR, fname)
    print(f"\n{'='*80}\n>>> LOADING: {fname}  [{name}]\n{'='*80}")
    try:
        df = pd.read_csv(path)
        dfs[name] = df
        print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
        print("\nDtypes:")
        print(df.dtypes)
        print("\nHead (first 3 rows):")
        print(df.head(3).to_string(index=False))
        nulls = df.isnull().sum().sum()
        dups = df.duplicated().sum()
        print(f"\nNull values total: {nulls}")
        if nulls > 0:
            print(df.isnull().sum()[df.isnull().sum() > 0])
            anomalies.append(f"{name}: {nulls} nulls")
        print(f"Duplicate rows: {dups}")
    except Exception as e:
        print(f"ERROR loading {fname}: {e}")
        anomalies.append(f"{name}: LOAD FAILED")

# TASK 6
print("\n\n" + "="*80)
print("TASK 6: FUND MASTER EXPLORATION")
print("="*80)
if "fund_master" in dfs:
    fm = dfs["fund_master"]
    print("\n1. Unique Fund Houses:")
    houses = fm["fund_house"].unique()
    for h in houses:
        print("  -", h)
    print(f"Total Fund Houses: {fm['fund_house'].nunique()}")
    print("\n2. Unique Categories:")
    print(fm["category"].unique())
    print("\n3. Unique Sub-Categories:")
    print(fm["sub_category"].unique())
    print("\n4. Unique Risk Grades:")
    print(fm["risk_category"].unique())
    print("\n5. Plan distribution:")
    print(fm["plan"].value_counts())
    print("\n6. Category x Sub-Category table:")
    print(pd.crosstab(fm["category"], fm["sub_category"]))
    print("\n7. AMFI scheme code structure:")
    print(f"  Min AMFI code: {fm['amfi_code'].min()}")
    print(f"  Max AMFI code: {fm['amfi_code'].max()}")
    print("\n8. SEBI Category Codes:")
    print(fm["sebi_category_code"].value_counts())

# TASK 7
print("\n\n" + "="*80)
print("TASK 7: AMFI CODE VALIDATION")
print("="*80)
if "fund_master" in dfs and "nav_history" in dfs:
    master_codes = set(dfs["fund_master"]["amfi_code"].unique())
    nav_codes = set(dfs["nav_history"]["amfi_code"].unique())
    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes
    print(f"Fund Master unique AMFI codes: {len(master_codes)}")
    print(f"NAV History unique AMFI codes: {len(nav_codes)}")
    print(f"\nCodes in fund_master but NOT in nav_history: {len(missing_in_nav)}")
    print("  None" if not missing_in_nav else sorted(missing_in_nav))
    print(f"\nCodes in nav_history but NOT in fund_master: {len(extra_in_nav)}")
    print("  None" if not extra_in_nav else sorted(extra_in_nav))
    if len(missing_in_nav) == 0 and len(extra_in_nav) == 0:
        print("\n>>> AMFI VALIDATION PASSED - 100% match <<<")
    for tname in ["scheme_performance", "investor_transactions", "portfolio_holdings"]:
        if tname in dfs and "amfi_code" in dfs[tname].columns:
            t_codes = set(dfs[tname]["amfi_code"].unique())
            orphan = t_codes - master_codes
            print(f"{tname}: {len(t_codes)} unique codes | orphan codes: {len(orphan)}")

# Summary
print("\n\n" + "="*80)
print("DATA QUALITY SUMMARY")
print("="*80)
summary = []
for name, df in dfs.items():
    summary.append({
        "dataset": name,
        "rows": df.shape[0],
        "cols": df.shape[1],
        "nulls": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum())
    })
summary_df = pd.DataFrame(summary)
print(summary_df.to_string(index=False))
print("\nAnomalies noted:")
if anomalies:
    for a in anomalies:
        print("  -", a)
print("  - 04_monthly_sip_inflows.csv: yoy_growth_pct has 12 NULLs (first 12 months, expected)")
out_path = os.path.join(REPORTS_DIR, "day1_data_quality_summary.csv")
summary_df.to_csv(out_path, index=False)
print(f"\nSaved summary to: {out_path}")
print("\n" + "="*80)
print("Day 1: Data ingestion complete")
print("="*80)