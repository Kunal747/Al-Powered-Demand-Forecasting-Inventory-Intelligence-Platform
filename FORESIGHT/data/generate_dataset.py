# -*- coding: utf-8 -*-
"""
Generates a synthetic Sales & Inventory dataset for Project FORESIGHT.
Intentionally messy: missing values, duplicates, outliers, inconsistent
text casing, and mixed date formats -- so it's usable for EDA practice
(cleaning, deduplication, missing-value handling) before feeding into
the forecasting pipeline.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

# ---------------------------------------------------------------
# 1. Master data: 25 SKUs across 5 categories, 4 regions
# ---------------------------------------------------------------
categories = ["Electronics", "Grocery", "Apparel", "Home & Kitchen", "Beauty"]
regions = ["North", "South", "East", "West"]

sku_master = []
sku_id = 1001
for cat in categories:
    for i in range(5):  # 5 SKUs per category -> 25 total
        sku_master.append({
            "SKU_ID": f"SKU{sku_id}",
            "SKU_Name": f"{cat.split()[0]}_Item_{i+1}",
            "Category": cat,
            "Unit_Price": round(rng.uniform(50, 2500), 2),
            "Lead_Time_Days": int(rng.integers(3, 21)),
            "Reorder_Level": int(rng.integers(20, 80)),
        })
        sku_id += 1
sku_master = pd.DataFrame(sku_master)

# ---------------------------------------------------------------
# 2. Weekly sales + inventory records, 2 years (104 weeks)
# ---------------------------------------------------------------
start_date = date(2024, 9, 1)
weeks = [start_date + timedelta(weeks=i) for i in range(104)]

records = []
for _, sku in sku_master.iterrows():
    base_demand = rng.uniform(30, 300)
    trend = rng.uniform(-0.15, 0.3)          # slow growth/decline per week
    season_amp = rng.uniform(0.1, 0.4)       # seasonality strength
    reorder_level = sku["Reorder_Level"]
    stock = reorder_level * rng.uniform(3, 5)  # realistic starting stock, a few weeks of cover

    for wi, wdate in enumerate(weeks):
        region = regions[rng.integers(0, 4)]

        seasonal = 1 + season_amp * np.sin(2 * np.pi * wi / 52)
        noise = rng.normal(1, 0.12)
        units_sold = max(0, base_demand * (1 + trend * wi / 104) * seasonal * noise)
        units_sold = round(units_sold)

        promo_flag = int(rng.random() < 0.08)
        if promo_flag:
            units_sold = round(units_sold * rng.uniform(1.3, 1.8))

        # Deplete stock with this week's sales
        stock = max(0, stock - units_sold)

        # Reorder-point logic: when stock falls below the SKU's reorder level,
        # place a replenishment order sized for ~6 weeks of average demand.
        # A minority of SKUs over-order occasionally, producing genuine overstock cases.
        if stock < reorder_level:
            order_qty = base_demand * rng.uniform(5, 7)
            if rng.random() < 0.12:  # occasional over-ordering -> overstock scenario
                order_qty *= rng.uniform(2.5, 4)
            stock += order_qty

        records.append({
            "Date": wdate.isoformat(),
            "SKU_ID": sku["SKU_ID"],
            "SKU_Name": sku["SKU_Name"],
            "Category": sku["Category"],
            "Region": region,
            "Units_Sold": units_sold,
            "Unit_Price": sku["Unit_Price"],
            "Current_Stock": round(stock, 1),
            "Reorder_Level": sku["Reorder_Level"],
            "Lead_Time_Days": sku["Lead_Time_Days"],
            "Promotion_Flag": promo_flag,
        })

df = pd.DataFrame(records)
df["Revenue"] = (df["Units_Sold"] * df["Unit_Price"]).round(2)

# ---------------------------------------------------------------
# 3. Inject realistic "messiness" for EDA practice
# ---------------------------------------------------------------

# 3a. Missing values (~4-6%) scattered across a few columns
for col, frac in [("Units_Sold", 0.05), ("Unit_Price", 0.03),
                   ("Current_Stock", 0.04), ("Region", 0.02)]:
    idx = df.sample(frac=frac, random_state=rng.integers(0, 1_000_000)).index
    df.loc[idx, col] = np.nan

# 3b. Duplicate rows (~2%) -- exact duplicates, common in raw exports
dup_rows = df.sample(frac=0.02, random_state=1).copy()
df = pd.concat([df, dup_rows], ignore_index=True)

# 3c. Inconsistent text casing / stray whitespace (common data-entry mess)
mask = df.sample(frac=0.1, random_state=2).index
df.loc[mask, "Category"] = df.loc[mask, "Category"].str.upper()
mask2 = df.sample(frac=0.08, random_state=3).index
df.loc[mask2, "Region"] = df.loc[mask2, "Region"].astype(str) + "  "  # trailing spaces

# 3d. Mixed date formats (some rows use DD-MM-YYYY string instead of ISO)
mask3 = df.sample(frac=0.06, random_state=4).index
def to_ddmmyyyy(iso_str):
    try:
        y, m, d = iso_str.split("-")
        return f"{d}-{m}-{y}"
    except Exception:
        return iso_str
df.loc[mask3, "Date"] = df.loc[mask3, "Date"].apply(to_ddmmyyyy)

# 3e. A few outliers / data-entry errors
out_idx = df.sample(n=15, random_state=5).index
df.loc[out_idx, "Units_Sold"] = df.loc[out_idx, "Units_Sold"] * rng.uniform(8, 15, size=15)

neg_idx = df.sample(n=6, random_state=6).index
df.loc[neg_idx, "Current_Stock"] = -abs(df.loc[neg_idx, "Current_Stock"])  # impossible negative stock

zero_price_idx = df.sample(n=5, random_state=7).index
df.loc[zero_price_idx, "Unit_Price"] = 0  # obviously wrong price entries

# 3f. Shuffle rows so duplicates/messiness aren't neatly grouped at the end
df = df.sample(frac=1, random_state=8).reset_index(drop=True)

# ---------------------------------------------------------------
# 4. Save outputs
# ---------------------------------------------------------------
df.to_csv("/home/claude/FORESIGHT/data/foresight_sales_inventory_raw.csv", index=False)
sku_master.to_csv("/home/claude/FORESIGHT/data/foresight_sku_master.csv", index=False)

print("Rows:", len(df))
print("Columns:", list(df.columns))
print("\nMissing values per column:\n", df.isna().sum())
print("\nExact duplicate rows:", df.duplicated().sum())
print(df.head(8))
