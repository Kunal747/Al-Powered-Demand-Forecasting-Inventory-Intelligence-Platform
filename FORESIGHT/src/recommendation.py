# -*- coding: utf-8 -*-
"""
recommendation.py
-------------------
WHAT: For every SKU flagged with Stockout risk, calculates how much to
      reorder right now. For Overstock SKUs, recommends holding off on
      ordering. For Normal SKUs, no action needed.
WHY : This is the "so what" layer -- forecasting + risk flags tell you
      *that* there's a problem, this module tells you *what to do about it*,
      which is the actual business value of the platform.
HOW : Classic inventory formula:
         Reorder Qty = Forecasted demand over lead time + Safety stock - Current stock
      Safety stock = a buffer (here, 50% of average weekly demand times lead-time weeks)
      to absorb demand variability, so we don't reorder to the bare minimum.

Run directly: python src/recommendation.py
"""
import pandas as pd
from datetime import datetime

from database import get_connection

SAFETY_STOCK_FACTOR = 0.5  # 50% buffer over the base lead-time demand


def run_recommendation_engine():
    conn = get_connection()

    risk_df = pd.read_sql("SELECT * FROM risk_alerts", conn)
    stock_df = pd.read_sql("""
        SELECT sh.sku_id, sh.current_stock, sh.lead_time_days
        FROM sales_history sh
        INNER JOIN (
            SELECT sku_id, MAX(date) AS max_date FROM sales_history GROUP BY sku_id
        ) latest ON sh.sku_id = latest.sku_id AND sh.date = latest.max_date
    """, conn)

    # risk_df already carries its own current_stock snapshot; drop it before
    # merging so we don't get ambiguous current_stock_x / current_stock_y columns
    merged = risk_df.drop(columns=["current_stock"]).merge(stock_df, on="sku_id")
    conn.execute("DELETE FROM recommendations")
    as_of = datetime.now().date().isoformat()
    rows = []

    for _, row in merged.iterrows():
        sku_id = row["sku_id"]
        demand_lt = row["forecasted_demand"]           # forecast over the lead-time window
        current_stock = row["current_stock"]
        safety_stock = round(demand_lt * SAFETY_STOCK_FACTOR, 1)

        if row["risk_type"] == "Stockout":
            reorder_qty = max(0, round(demand_lt + safety_stock - current_stock, 1))
            reasoning = (
                f"Forecasted demand over lead time ({demand_lt}) plus safety stock "
                f"({safety_stock}) exceeds current stock ({current_stock}). "
                f"Order now to avoid running out before the next delivery arrives."
            )
        elif row["risk_type"] == "Overstock":
            reorder_qty = 0
            reasoning = (
                f"Current stock ({current_stock}) already far exceeds forecasted demand "
                f"({demand_lt}). Hold new orders and monitor sell-through before reordering."
            )
        else:
            reorder_qty = 0
            reasoning = "Stock is within a healthy range relative to forecasted demand. No action needed."

        rows.append((sku_id, as_of, reorder_qty, safety_stock, reasoning))

    conn.executemany(
        """INSERT INTO recommendations
           (sku_id, as_of_date, recommended_reorder_qty, safety_stock, reasoning)
           VALUES (?, ?, ?, ?, ?)""",
        rows
    )
    conn.commit()

    result = pd.read_sql("SELECT sku_id, recommended_reorder_qty, safety_stock FROM recommendations", conn)
    conn.close()

    print(f"Recommendations generated for {len(result)} SKUs.")
    print(f"SKUs needing reorder: {(result['recommended_reorder_qty'] > 0).sum()}")
    return result


if __name__ == "__main__":
    run_recommendation_engine()
