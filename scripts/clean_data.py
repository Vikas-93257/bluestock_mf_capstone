"""
Day 2 – Data Cleaning
Bluestock Fintech – Mutual Fund Analytics Capstone
Author: Vikas Maurya
Date: 26 Jun 2026
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("="*70)
print("BLUESTOCK MF – DAY 2 DATA CLEANING")
print("="*70)

# ========== TASK 1 – Clean nav_history.csv ==========
print("\n[TASK 1] Cleaning nav_history.csv")
print("  - Parse dates to datetime")
print("  - Sort by amfi_code + date")
print("  - Forward-fill missing NAV")
print("  - Remove duplicates")
print("  - Validate NAV > 0")
print("-"*60)

# parse dates to datetime – PDF Task 1 – point 1
df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"), parse_dates=["date"])
print(f"Input rows: {df.shape[0]}")
print(f"Date column type: {df['date'].dtype}")

# Sort by amfi_code + date – PDF Task 1 – point 2
df = df.sort_values(["amfi_code", "date"])
print(f"Sorted – first row: amfi_code={df.iloc[0]['amfi_code']}, date={df.iloc[0]['date'].date()}, nav={df.iloc[0]['nav']}")

# Remove duplicates – PDF Task 1 – point 4
dups = df.duplicated().sum()
print(f"Duplicates found: {dups}")
df = df.drop_duplicates()
print(f"After dropping duplicates: {df.shape[0]} rows")

# Validate NAV > 0 – PDF Task 1 – point 5
bad_nav = (df["nav"] <= 0).sum()
print(f"NAV <= 0 found: {bad_nav}")
df = df[df["nav"] > 0]
print(f"After NAV > 0 filter: {df.shape[0]} rows")


# Forward-fill missing NAV for holidays/weekends – PDF Task 1 – point 3
print("\nForward-filling holidays...")
print(f"  Date range in data: {df['date'].min().date()} to {df['date'].max().date()}")

cleaned_list = []

# har amfi_code ke liye alag loop – 40 funds
for code in df["amfi_code"].unique():
    # 1. is fund ka data nikaalo
    fund_df = df[df["amfi_code"] == code].copy()
    
    # 2. date ko index banao – taaki reindex kar sake
    fund_df = fund_df.set_index("date")
    fund_df = fund_df.sort_index()
    
    # 3. poora calendar banao – daily – including weekends
    #    start = pehla NAV date, end = aakhri NAV date
    full_calendar = pd.date_range(
        start=fund_df.index.min(),
        end=fund_df.index.max(),
        freq="D"
    )
    
    # 4. reindex – missing dates (Sat/Sun) → NaN
    fund_df = fund_df.reindex(full_calendar)
    
    # 5. amfi_code bhar do – reindex se NaN ho gaya tha
    fund_df["amfi_code"] = code
    
    # 6. forward-fill – aaj ka NAV = kal ka NAV
    #    ffill = forward fill
    before_ffill = fund_df["nav"].isnull().sum()
    fund_df["nav"] = fund_df["nav"].ffill()
    after_ffill = fund_df["nav"].isnull().sum()
    
    # pehli baar bolega kitna fill hua – baaki 39 funds silent
    if code == df["amfi_code"].unique()[0]:
        print(f"  Example fund {code}:")
        print(f"    Trading days in raw: {len(pd.read_csv('data/raw/02_nav_history.csv').query(f'amfi_code=={code}'))}")
        print(f"    Calendar days (with weekends): {len(fund_df)}")
        print(f"    Missing NAV (weekends/holidays) filled: {before_ffill} → {after_ffill}")
    
    # 7. index wapas date column banao
    fund_df = fund_df.reset_index()
    fund_df = fund_df.rename(columns={"index": "date"})
    
    # 8. list me daalo
    cleaned_list.append(fund_df)

# 9. sab 40 funds ko jod do
df_nav_clean = pd.concat(cleaned_list, ignore_index=True)

# 10. column order theek karo – amfi_code, date, nav
df_nav_clean = df_nav_clean[["amfi_code", "date", "nav"]]

# 11. date ko YYYY-MM-DD string banao – CSV save karne ke liye
df_nav_clean["date"] = pd.to_datetime(df_nav_clean["date"]).dt.strftime("%Y-%m-%d")

print(f"\n  BEFORE ffill: {df.shape[0]} rows (trading days only)")
print(f"  AFTER ffill:  {df_nav_clean.shape[0]} rows (including weekends/holidays)")
print(f"  Added rows: {df_nav_clean.shape[0] - df.shape[0]} (holiday fills)")

# 12. SAVE – Bluestock deliverable: clean_nav_history.csv in data/processed/
import os
output_path = "data/processed/clean_nav_history.csv"
os.makedirs("data/processed", exist_ok=True)
df_nav_clean.to_csv(output_path, index=False)
print(f"\n  ✓ Saved: {output_path}")
print(f"  ✓ File size: {os.path.getsize(output_path)/1024:.1f} KB")

print("\n" + "="*70)
print("TASK 1 COMPLETE – nav_history cleaned")
print("="*70)


# ========== TASK 2 – Clean investor_transactions.csv ==========
print("\n" + "="*70)
print("TASK 2: CLEAN investor_transactions.csv")
print("  - Standardise transaction_type")
print("  - Validate amount > 0")
print("  - Fix date formats")
print("  - Check KYC status enum")
print("="*70)

import pandas as pd

# load raw
df_tx = pd.read_csv("data/raw/08_investor_transactions.csv")
print(f"\nInput rows: {df_tx.shape[0]}")
print(f"Columns: {list(df_tx.columns)}")

# check transaction_type values BEFORE cleaning
print("\n--- transaction_type BEFORE ---")
print(df_tx["transaction_type"].value_counts())



# 1. Standardise transaction_type values (SIP/Lumpsum/Redemption)
# PDF Task 2 – point 1
print("\n--- Step 1: Standardise transaction_type ---")
# make lower, strip spaces, then map to proper case
df_tx["transaction_type"] = df_tx["transaction_type"].astype(str).str.strip()
df_tx["transaction_type"] = df_tx["transaction_type"].str.lower()

# mapping dict – handles SIP, sip, Sip, LUMPSUM, lumpsum, etc
type_map = {
    "sip": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "lump_sum": "Lumpsum",
    "redemption": "Redemption",
    "redeem": "Redemption",
    "withdrawal": "Redemption",
    "switch out": "Redemption"
}
# apply map – if not found, Title case fallback
df_tx["transaction_type"] = df_tx["transaction_type"].map(type_map).fillna(
    df_tx["transaction_type"].str.title()
)

print("After standardisation:")
print(df_tx["transaction_type"].value_counts())

# 2. Validate amount > 0 – PDF Task 2 – point 2
print("\n--- Step 2: Validate amount > 0 ---")
bad_amount = (df_tx["amount_inr"] <= 0).sum()
print(f"amount_inr <= 0 found: {bad_amount}")
if bad_amount > 0:
    print(df_tx[df_tx["amount_inr"] <= 0].head())
df_tx = df_tx[df_tx["amount_inr"] > 0]
print(f"Rows after amount filter: {df_tx.shape[0]}")

# 3. Fix date formats – PDF Task 2 – point 3
print("\n--- Step 3: Fix date formats ---")
print(f"transaction_date dtype before: {df_tx['transaction_date'].dtype}")
df_tx["transaction_date"] = pd.to_datetime(
    df_tx["transaction_date"], 
    errors="coerce"
)
bad_dates = df_tx["transaction_date"].isna().sum()
print(f"Invalid dates found: {bad_dates}")
df_tx = df_tx.dropna(subset=["transaction_date"])
# save back as YYYY-MM-DD string for SQLite
df_tx["transaction_date"] = df_tx["transaction_date"].dt.strftime("%Y-%m-%d")
print(f"transaction_date fixed – sample: {df_tx['transaction_date'].iloc[0]}")
print(f"Rows after date fix: {df_tx.shape[0]}")

# 4. Check KYC status enum values – PDF Task 2 – point 4
print("\n--- Step 4: Check KYC status enum values ---")
kyc_values = df_tx["kyc_status"].unique()
print(f"KYC status values found: {kyc_values.tolist()}")
kyc_counts = df_tx["kyc_status"].value_counts()
print(kyc_counts)
# Bluestock expected enum: Verified / Pending / Rejected ?
# Document what you found
valid_kyc = ["Verified", "Pending", "Rejected", "verified", "pending"]
invalid_kyc = [x for x in kyc_values if x not in valid_kyc and str(x).title() not in ["Verified","Pending","Rejected"]]
if invalid_kyc:
    print(f"WARNING – unexpected KYC values: {invalid_kyc}")
else:
    print("✓ All KYC values are in expected enum")

# Final – remove duplicates
print("\n--- Final cleanup ---")
dups = df_tx.duplicated().sum()
print(f"Duplicates found: {dups}")
df_tx = df_tx.drop_duplicates()
print(f"Final output rows: {df_tx.shape[0]}")

# Save – Bluestock deliverable
output_path = "data/processed/clean_transaction.csv"
df_tx.to_csv(output_path, index=False)
print(f"\n✓ Saved: {output_path}")
print(f"✓ File size: {__import__('os').path.getsize(output_path)/1024:.1f} KB")

print("\n" + "="*70)
print("TASK 2 COMPLETE – investor_transactions cleaned")
print("="*70)



# ========== TASK 3 – Clean scheme_performance.csv ==========
print("\n" + "="*70)
print("TASK 3: CLEAN scheme_performance.csv")
print("  - Validate all return values are numeric")
print("  - Flag anomalies")
print("  - Check expense_ratio range (0.1% – 2.5%)")
print("="*70)

import pandas as pd

# load
df_perf = pd.read_csv("data/raw/07_scheme_performance.csv")
print(f"\nInput rows: {df_perf.shape[0]}")

# 1. Validate all return values are numeric – PDF Task 3 point 1
num_cols = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta",
    "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct", "morningstar_rating"
]

print("\n--- Validating numeric columns ---")
for col in num_cols:
    # pd.to_numeric – string → number – errors='coerce' → bad value → NaN
    df_perf[col] = pd.to_numeric(df_perf[col], errors="coerce")

null_count = df_perf[num_cols].isnull().sum().sum()
print(f"Numeric coercion nulls found: {null_count}")
if null_count > 0:
    print(df_perf[num_cols].isnull().sum())
else:
    print("✓ All return values are numeric – 0 nulls")

# 2. Flag anomalies – PDF Task 3 point 2
print("\n--- Flag anomalies ---")

# Sharpe ratio negative = fund losing money vs risk-free
neg_sharpe = df_perf[df_perf["sharpe_ratio"] < 0]
print(f"Negative Sharpe ratios flagged: {len(neg_sharpe)}")
if len(neg_sharpe) > 0:
    print(neg_sharpe[["amfi_code", "scheme_name", "sharpe_ratio"]].to_string(index=False))
else:
    print("  → None – all Sharpe >= 0  ✓")

# Alpha very negative = underperforming benchmark badly
neg_alpha = df_perf[df_perf["alpha"] < -2]
print(f"\nAlpha < -2 flagged: {len(neg_alpha)}")
if len(neg_alpha) > 0:
    print(neg_alpha[["amfi_code", "scheme_name", "alpha"]].to_string(index=False))

# Beta extreme check
high_beta = df_perf[df_perf["beta"] > 1.5]
print(f"\nBeta > 1.5 flagged (very volatile): {len(high_beta)}")

# 3. Check expense_ratio range (0.1% – 2.5%) – PDF Task 3 point 3
print("\n--- Check expense_ratio range (0.1% – 2.5%) ---")
oor = df_perf[~df_perf["expense_ratio_pct"].between(0.1, 2.5)]
print(f"expense_ratio out of 0.1-2.5% range: {len(oor)}")
if len(oor) > 0:
    print(oor[["amfi_code", "scheme_name", "expense_ratio_pct"]].to_string(index=False))
else:
    print("✓ All expense ratios in valid SEBI range 0.1% – 2.5%")

# Check Morningstar rating range 1-5
bad_rating = df_perf[~df_perf["morningstar_rating"].between(1, 5)]
print(f"\nMorningstar rating out of 1-5: {len(bad_rating)}")

print(f"\nOutput rows: {df_perf.shape[0]}")
# save
df_perf.to_csv("data/processed/clean_performance.csv", index=False)
print("✓ Saved: data/processed/clean_performance.csv")

import os
size_kb = os.path.getsize("data/processed/clean_performance.csv") / 1024
print(f"✓ File size: {size_kb:.1f} KB")

print("\n" + "="*70)
print("TASK 3 COMPLETE – scheme_performance cleaned")
print("="*70)


# ========== TASK 3B – Clean remaining 7 files ==========
print("\n" + "="*70)
print("Cleaning remaining 7 datasets...")
print("="*70)

import os
clean_jobs = [
    # raw_file, clean_file, date_cols to parse
    ("01_fund_master.csv", "clean_fund_master.csv", ["launch_date"]),
    ("03_aum_by_fund_house.csv", "clean_aum.csv", ["date"]),
    ("04_monthly_sip_inflows.csv", "clean_sip_inflows.csv", []),
    ("05_category_inflows.csv", "clean_category_inflows.csv", []),
    ("06_industry_folio_count.csv", "clean_folio_count.csv", []),
    ("09_portfolio_holdings.csv", "clean_portfolio.csv", ["portfolio_date"]),
    ("10_benchmark_indices.csv", "clean_benchmark.csv", ["date"]),
]

for i, (raw_file, clean_file, date_cols) in enumerate(clean_jobs, start=4):
    print(f"\n[{i}/10] {raw_file} → {clean_file}")
    in_path = os.path.join("data", "raw", raw_file)
    df = pd.read_csv(in_path)
    print(f"  Input: {df.shape[0]} rows × {df.shape[1]} cols")

    # date parse
    for dc in date_cols:
        if dc in df.columns:
            df[dc] = pd.to_datetime(df[dc], errors="coerce").dt.strftime("%Y-%m-%d")

    # Day 1 anomaly fix – monthly_sip_inflows – yoy_growth_pct 12 NULLs
    if raw_file == "04_monthly_sip_inflows.csv":
        nulls_before = df["yoy_growth_pct"].isnull().sum()
        print(f"  yoy_growth_pct NULLs before: {nulls_before}")
        # forward-fill then 0 fill
        df["yoy_growth_pct"] = df["yoy_growth_pct"].ffill().fillna(0)
        print(f"  yoy_growth_pct NULLs after: {df['yoy_growth_pct'].isnull().sum()}  ✅ fixed")

    # remove duplicates
    dups = df.duplicated().sum()
    df = df.drop_duplicates()

    nulls = df.isnull().sum().sum()
    out_path = os.path.join("data", "processed", clean_file)
    df.to_csv(out_path, index=False)
    print(f"  Dups removed: {dups} | Nulls: {nulls} | Output: {df.shape[0]} rows")
    print(f"  ✓ Saved: {out_path}")

# ========== FINAL SUMMARY ==========
print("\n" + "="*80)
print("DAY 2 DATA CLEANING COMPLETE")
print("="*80)

import glob
cleaned = sorted(glob.glob("data/processed/clean_*.csv"))
print(f"Cleaned files: {len(cleaned)}/10\n")
for f in cleaned:
    dft = pd.read_csv(f)
    print(f"  ✓ {os.path.basename(f):30} {dft.shape[0]:>6} rows × {dft.shape[1]} cols | nulls: {dft.isnull().sum().sum()}")
print("\nNext step: SQL schema design → sql/schema.sql")
print("="*80)