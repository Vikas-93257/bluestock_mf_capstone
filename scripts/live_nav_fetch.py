"""
Live NAV Fetcher – Day 1 Task 4 & 5
Bluestock Fintech – Mutual Fund Analytics Capstone
Author: Vikas
Intern – Bluestock Fintech, Pune
Date: 25 Jun 2026
API: https://api.mfapi.in
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data", "raw")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Task 4 + Task 5
# Task 4: Fetch live NAV from mfapi.in: GET https://api.mfapi.in/mf/125497 (HDFC Top 100 Direct)
# Task 5: Fetch NAV for 5 key schemes
funds = {
    "HDFC_TOP_100": "125497",      # Task 4
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

print("="*70)
print("BLUESTOCK MF ANALYTICS – LIVE NAV FETCH")
print(f"Fetch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("API: https://api.mfapi.in/mf/{scheme_code}")
print("="*70)

results = []

for name, code in funds.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"\nFetching: {name} (AMFI: {code})...")
    print(f"  GET {url}")
    try:
        response = requests.get(url, timeout=30)
        print(f"  HTTP Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            meta = data.get("meta", {})
            nav_data = data.get("data", [])

            # Parse JSON response – Task 4 requirement
            print(f"  Scheme Name (API): {meta.get('scheme_name', 'N/A')}")
            print(f"  Fund House (API): {meta.get('fund_house', 'N/A')}")
            print(f"  Records: {len(nav_data)}")

            if nav_data:
                df = pd.DataFrame(nav_data)

                # Save as raw CSV – Task 4 requirement
                file_path = os.path.join(OUTPUT_FOLDER, f"{code}_{name}_live.csv")
                df.to_csv(file_path, index=False)

                latest_nav = df.iloc[0]["nav"]
                latest_date = df.iloc[0]["date"]
                print(f"  Latest NAV: {latest_nav} on {latest_date}")
                print(f"  Saved to: {file_path}")
                print("  Status: SUCCESS")

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
                print("  No NAV data found")
                results.append({"fund_name": name, "amfi_code": code, "status": "NO_DATA", "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})
        else:
            print(f"  Failed. Status: {response.status_code}")
            results.append({"fund_name": name, "amfi_code": code, "status": f"HTTP_{response.status_code}", "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})
    except Exception as e:
        print(f"  Error: {e}")
        results.append({"fund_name": name, "amfi_code": code, "status": str(e), "records": 0, "latest_nav": "", "latest_date": "", "scheme_name_api": "", "fund_house_api": ""})

    time.sleep(1)

print("\n" + "="*70)
print("FETCH SUMMARY")
print("="*70)
summary_df = pd.DataFrame(results)
print(summary_df.to_string(index=False))

log_path = os.path.join(REPORTS_DIR, "live_nav_fetch_summary.csv")
summary_df.to_csv(log_path, index=False)
print(f"\nLog saved: {log_path}")
print("\nAll live data fetching completed!")
print("="*70)
