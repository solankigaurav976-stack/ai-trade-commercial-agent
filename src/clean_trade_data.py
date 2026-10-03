from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "ots_exports_2025_2026.csv"
OUTPUT_FILE = BASE_DIR / "data" / "ots_clean_2026.csv"

print("Loading OTS data...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")
print("\nColumns:")
print(df.columns.tolist())

# -----------------------------
# Data types
# -----------------------------

df["MonthId"] = pd.to_numeric(df["MonthId"], errors="coerce")
df["FlowTypeId"] = pd.to_numeric(df["
                                    
FlowTypeId"], errors="coerce")
df["CommodityId"] = pd.to_numeric(df["CommodityId"], errors="coerce")
df["CountryId"] = pd.to_numeric(df["CountryId"], errors="coerce")
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df["NetMass"] = pd.to_numeric(df["NetMass"], errors="coerce")

# -----------------------------
# Date
# -----------------------------

df["Date"] = pd.to_datetime(
    df["MonthId"].astype("Int64").astype(str),
    format="%Y%m",
    errors="coerce"
)

# -----------------------------
# Basic validation
# -----------------------------

print("\nMissing values:")
print(df.isna().sum())

print("\nFlow types:")
print(df["FlowTypeId"].value_counts().sort_index())

print("\nDate range:")
print(df["Date"].min())
print(df["Date"].max())

print("\nUnique countries:")
print(df["CountryId"].nunique())

print("\nUnique commodities:")
print(df["CommodityId"].nunique())

# -----------------------------
# Remove unusable rows
# -----------------------------

df = df.dropna(
    subset=[
        "MonthId",
        "FlowTypeId",
        "CommodityId",
        "CountryId",
        "Value"
    ]
)

# Trade values should not be negative
df = df[df["Value"] >= 0]

# -----------------------------
# Save
# -----------------------------

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nClean records: {len(df):,}")
print(f"Saved to: {OUTPUT_FILE}")
