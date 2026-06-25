"""
Day 1 – Data Ingestion (ETL)
Bluestock Fintech – Mutual Fund Analytics Capstone
Author: Vikas
Intern – Bluestock Fintech, Pune
Date: 20 Jun 2026
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

print("="*80)
print("BLUESTOCK MUTUAL FUND ANALYTICS – DAY 1 DATA INGESTION")
print("Project: Capstone Project I - Mutual Fund Analytics")
print("Date: 20 Jun 2026")
print("="*80)

# Task 3 – Load all 10 CSV datasets
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

dfs = {}
anomalies = []

for name, fname in files.items():
    path = os.path.join(RAW_DIR, fname)
    print(f"\n{'='*80}\n>>> LOADING: {fname}  [{name}]\n{'='*80}")
    df = pd.read_csv(path)
    dfs[name] = df

    # Bluestock Task 3 – required prints
    print(f".shape: {df.shape}")
    print("\n.dtypes:")
    print(df.dtypes)
    print("\n.head():")
    print(df.head(3).to_string(index=False))

    nulls = df.isnull().sum().sum()
    dups = df.duplicated().sum()
    print(f"\nNulls total: {nulls}")
    if nulls > 0:
        print(df.isnull().sum()[df.isnull().sum() > 0])
        anomalies.append(f"{name}: {nulls} nulls")
    print(f"Duplicates: {dups}")

# TASK 6 – Explore fund master
print("\n\n" + "="*80)
print("TASK 6: FUND MASTER EXPLORATION")
print("="*80)
fm = dfs["fund_master"]

print("\nUnique Fund Houses:")
print(fm["fund_house"].unique())
print(f"Total Fund Houses: {fm['fund_house'].nunique()}")

print("\nUnique Categories:")
print(fm["category"].unique())

print("\nUnique Sub-Categories:")
print(fm["sub_category"].unique())

print("\nUnique Risk Grades:")
print(fm["risk_category"].unique())

print("\nPlan distribution:")
print(fm["plan"].value_counts())

print("\nCategory x Sub-Category Cross-tab:")
print(pd.crosstab(fm["category"], fm["sub_category"]))

print("\nAMFI scheme code structure:")
print(f"Min AMFI code: {fm['amfi_code'].min()}")
print(f"Max AMFI code: {fm['amfi_code'].max()}")
print("\nSample codes:")
print(fm[["amfi_code", "scheme_name", "fund_house"]].head(10).to_string(index=False))

print("\nSEBI Category Codes:")
print(fm["sebi_category_code"].value_counts())

# TASK 7 – Validate AMFI codes
print("\n\n" + "="*80)
print("TASK 7: AMFI CODE VALIDATION")
print("="*80)
master_codes = set(dfs["fund_master"]["amfi_code"].unique())
nav_codes = set(dfs["nav_history"]["amfi_code"].unique())
missing_in_nav = master_codes - nav_codes
extra_in_nav = nav_codes - master_codes

print(f"Fund Master unique AMFI codes: {len(master_codes)}")
print(f"NAV History unique AMFI codes: {len(nav_codes)}")
print(f"\nCodes in fund_master but NOT in nav_history: {len(missing_in_nav)}")
if missing_in_nav:
    print(sorted(missing_in_nav))
else:
    print("  None")
print(f"\nCodes in nav_history but NOT in fund_master: {len(extra_in_nav)}")
if extra_in_nav:
    print(sorted(extra_in_nav))
else:
    print("  None")

if len(missing_in_nav) == 0 and len(extra_in_nav) == 0:
    print("\n>>> AMFI VALIDATION PASSED - 100% match <<<")

# Cross-check other tables
for tname in ["scheme_performance", "investor_transactions", "portfolio_holdings"]:
    if tname in dfs and "amfi_code" in dfs[tname].columns:
        t_codes = set(dfs[tname]["amfi_code"].unique())
        orphan = t_codes - master_codes
        print(f"\n{tname}: {len(t_codes)} unique codes | orphan codes: {len(orphan)}")

# Data Quality Summary – Task 7
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
print("\nDay 1: Data ingestion complete")
