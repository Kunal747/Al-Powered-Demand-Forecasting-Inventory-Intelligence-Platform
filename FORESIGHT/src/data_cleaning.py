# -*- coding: utf-8 -*-
"""
data_cleaning.py
-----------------
WHAT: Cleans the raw, messy sales & inventory export into an analysis-ready dataset.
WHY : Real-world exports always have duplicates, missing values, inconsistent text
      and mixed date formats. Forecasting models (ARIMA etc.) will produce wrong
      or crashing results if fed dirty data, so this is the first pipeline stage.
HOW : Uses pandas for all cleaning operations (dedup, imputation, standardisation).

Run directly:  python src/data_cleaning.py
"""
import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "foresight_sales_inventory_raw.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "foresight_sales_inventory_clean.csv")


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Some rows use ISO (YYYY-MM-DD), others DD-MM-YYYY. Try ISO first, then DD-MM-YYYY."""
    parsed = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")
    still_missing = parsed.isna()
    parsed.loc[still_missing] = pd.to_datetime(
        series.loc[still_missing], format="%d-%m-%Y", errors="coerce"
    )
    return parsed


def clean_dataset(raw_path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(raw_path)

    # 1. Standardise text columns: strip whitespace, fix inconsistent casing
    df["Category"] = df["Category"].astype(str).str.strip().str.title()
    df["Region"] = df["Region"].astype(str).str.strip().str.title()
    df.loc[df["Region"].isin(["Nan", "None"]), "Region"] = np.nan

    # 2. Parse mixed date formats into a single proper datetime column
    df["Date"] = parse_mixed_dates(df["Date"])

    # 3. Drop exact duplicate rows (common in raw exports / repeated uploads)
    before = len(df)
    df = df.drop_duplicates()
    dupes_removed = before - len(df)

    # 4. Fix impossible values
    #    - Negative stock is a data-entry error -> treat as missing, then impute
    df.loc[df["Current_Stock"] < 0, "Current_Stock"] = np.nan
    #    - Zero price is invalid for a sold item -> treat as missing, then impute
    df.loc[df["Unit_Price"] <= 0, "Unit_Price"] = np.nan

    # 5. Cap extreme outliers in Units_Sold using the IQR method
    #    (keeps genuine demand spikes but tames data-entry-error-level extremes)
    q1, q3 = df["Units_Sold"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_bound = q3 + 3 * iqr
    outliers_capped = (df["Units_Sold"] > upper_bound).sum()
    df.loc[df["Units_Sold"] > upper_bound, "Units_Sold"] = upper_bound

    # 6. Impute missing values
    #    - Numeric columns: fill with the median for that SKU (keeps SKU-level scale correct)
    for col in ["Units_Sold", "Unit_Price", "Current_Stock"]:
        df[col] = df.groupby("SKU_ID")[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median())  # fallback if a whole SKU group was NaN

    #    - Region: fill with the most frequent region for that SKU, else global mode
    def fill_region(group):
        mode = group.mode()
        return group.fillna(mode.iloc[0] if not mode.empty else "Unknown")
    df["Region"] = df.groupby("SKU_ID")["Region"].transform(fill_region)

    # 7. Recompute Revenue after cleaning Units_Sold / Unit_Price so it's internally consistent
    df["Revenue"] = (df["Units_Sold"] * df["Unit_Price"]).round(2)

    # 8. Drop rows where Date failed to parse entirely (should be ~0 after step 2)
    unparsed_dates = df["Date"].isna().sum()
    df = df.dropna(subset=["Date"])

    # 9. Sort for readability / downstream time-series processing
    df = df.sort_values(["SKU_ID", "Date"]).reset_index(drop=True)

    print("---- Cleaning summary ----")
    print(f"Duplicate rows removed : {dupes_removed}")
    print(f"Units_Sold outliers capped (IQR method) : {outliers_capped}")
    print(f"Rows dropped for unparseable dates : {unparsed_dates}")
    print(f"Final row count : {len(df)}")
    print(f"Remaining missing values:\n{df.isna().sum()[df.isna().sum() > 0]}")

    return df


if __name__ == "__main__":
    cleaned = clean_dataset()
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"\nClean dataset saved to: {CLEAN_PATH}")
