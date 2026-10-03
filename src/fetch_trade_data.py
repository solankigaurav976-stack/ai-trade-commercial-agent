import requests
import pandas as pd
from pathlib import Path

BASE_URL = "https://api.uktradeinfo.com"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_api_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"

    print(f"Connecting to HMRC UK Trade Info API...")
    response = requests.get(
        url,
        params=params,
        timeout=120
    )

    print(f"Status: {response.status_code}")

    response.raise_for_status()

    data = response.json()

    return data.get("value", [])


def main():

    # 2025 January to 2026 July
    params = {
        "$filter": (
            "MonthId ge 202501 "
            "and MonthId le 202607 "
            "and (FlowTypeId eq 2 or FlowTypeId eq 4)"
        ),
        "$select": (
            "MonthId,"
            "FlowTypeId,"
            "CommodityId,"
            "CountryId,"
            "Value,"
            "NetMass"
        ),
        "$top": 40000
    }

    records = get_api_data("OTS", params)

    print(f"\nRecords retrieved: {len(records):,}")

    if not records:
        print("No records returned.")
        return

    df = pd.DataFrame(records)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst records:")
    print(df.head())

    output_file = OUTPUT_DIR / "ots_exports_2025_2026.csv"

    df.to_csv(output_file, index=False)

    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()