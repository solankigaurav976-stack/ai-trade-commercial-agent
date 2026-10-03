import requests
import pandas as pd
from pathlib import Path

BASE_URL = "https://api.uktradeinfo.com"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_metadata(endpoint):
    url = f"{BASE_URL}/{endpoint}"

    print(f"\nFetching: {endpoint}")

    response = requests.get(url, timeout=60)

    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    return data.get("value", [])


def save_metadata(endpoint, filename):

    records = get_metadata(endpoint)

    print("Records:", len(records))

    df = pd.DataFrame(records)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst records:")
    print(df.head(10))

    output_file = OUTPUT_DIR / filename

    df.to_csv(output_file, index=False)

    print(f"\nSaved to: {output_file}")


def main():

    save_metadata(
        "Country",
        "countries.csv"
    )

    save_metadata(
        "Commodity",
        "commodities.csv"
    )

    save_metadata(
        "FlowType",
        "flow_types.csv"
    )


if __name__ == "__main__":
    main()