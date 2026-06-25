"""
Live NAV Fetcher – Day 1 Task 4 & 5
Bluestock Fintech – Mutual Fund Analytics Capstone
API: https://www.mfapi.in/
Author: Vikas
Date: 25 Jun 2026
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime

# find project folders automatically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data", "raw")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Task 4 + Task 5 – 6 funds from Bluestock PDF
funds = {
    "HDFC_TOP_100": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

print("="*60)
print("Bluestock MF Analytics – Live NAV Fetch")
print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("API: https://api.mfapi.in/mf/{scheme_code}")
print("="*60)

results = []

for name, code in funds.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"\nFetching: {name}  (AMFI: {code})")
    print(f"  URL: {url}")
    try:
        response = requests.get(url, timeout=30)
        print(f"  HTTP Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            meta = data.get("meta", {})
            nav_data = data.get("data", [])

            print(f"  Scheme Name (API): {meta.get('scheme_name', 'N/A')}")
            print(f"  Fund House (API): {meta.get('fund_house', 'N/A')}")
            print(f"  Records found: {len(nav_data)}")

            if nav_data:
                df = pd.DataFrame(nav_data)
                # save exactly as Bluestock wants
                file_path = os.path.join(OUTPUT_FOLDER, f"{code}_{name}_live.csv")
                df.to_csv(file_path, index=False)

                latest_nav = df.iloc[0]["nav"]
                latest_date = df.iloc[0]["date"]
                print(f"  Latest NAV: {latest_nav}  on {latest_date}")
                print(f"  Saved to: {file_path}")
                print("  Status: SUCCESS ✓")

                results.append({
                    "fund_name": name,
                    "amfi_code": code,
                    "scheme_name_api": meta.get("scheme_name", ""),
                    "fund_house_api": meta.get("fund_house", ""),
                    "records": len(df),
                    "latest_nav": latest_nav,
                    "latest_date": latest_date,
                    "status": "SUCCESS"
                })
            else:
                print("  Status: NO DATA")
                results.append({"fund_name": name, "amfi_code": code, "status": "NO_DATA", "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})
        else:
            print(f"  Status: FAILED HTTP {response.status_code}")
            results.append({"fund_name": name, "amfi_code": code, "status": f"HTTP_{response.status_code}", "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})

    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({"fund_name": name, "amfi_code": code, "status": f"ERROR {e}", "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})

    time.sleep(1)  # be polite to API, 1 sec gap

# Summary table
print("\n" + "="*60)
print("FETCH SUMMARY")
print("="*60)
summary_df = pd.DataFrame(results)
print(summary_df.to_string(index=False))

# save log
log_path = os.path.join(REPORTS_DIR, "live_nav_fetch_summary.csv")
summary_df.to_csv(log_path, index=False)
print(f"\nLog saved: {log_path}")
print("\nAll live data fetching completed! ✅")
print("="*60)