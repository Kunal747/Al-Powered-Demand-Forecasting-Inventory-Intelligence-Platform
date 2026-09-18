# -*- coding: utf-8 -*-
"""
risk_detection.py
-------------------
WHAT: Compares each SKU's current stock against its forecasted near-term
      demand and flags it as at risk of Stockout, Overstock, or Normal.
WHY : A forecast number alone isn't actionable -- a manager needs a clear
      flag ("this SKU will run out in ~2 weeks") to act on, which is the
      whole point of an "inventory intelligence" platform.
HOW : Rule-based logic (deliberately simple & explainable, not a black box):
      - Stockout risk  : current stock < forecasted demand for the lead-time window
      - Overstock risk : current stock > 3x the forecasted demand for the same window
      - Risk level (High/Medium/Low) scales with how far past the threshold it is.

Run directly: python src/risk_detection.py
"""
import pandas as pd
from datetime import datetime

from database import get_connection


def classify_risk(current_stock, forecast_demand, lead_time_days):
    """Returns (risk_type, risk_level)."""
    if forecast_demand <= 0:
        return "Normal", "Low"

    coverage_ratio = current_stock / forecast_demand  # how many "demand-periods" of stock we hold

    if current_stock < forecast_demand:
        # Will likely run out before lead time to restock passes
        shortfall_pct = (forecast_demand - current_stock) / forecast_demand
        level = "High" if shortfall_pct > 0.5 else "Medium"
        return "Stockout", level

    elif coverage_ratio > 3:
        excess_pct = (current_stock - forecast_demand) / forecast_demand
        level = "High" if excess_pct > 5 else "Medium"
        return "Overstock", level

    else:
        return "Normal", "Low"


def run_risk_detection():
    conn = get_connection()

    # Latest known stock per SKU (most recent sales_history row)
    latest_stock = pd.read_sql("""
        SELECT sh.sku_id, sh.current_stock, sh.lead_time_days, sh.date
        FROM sales_history sh
        INNER JOIN (
            SELECT sku_id, MAX(date) AS max_date FROM sales_history GROUP BY sku_id
        ) latest ON sh.sku_id = latest.sku_id AND sh.date = latest.max_date
    """, conn)

    # Forecast demand over each SKU's own lead-time window (in weeks, rounded up)
    forecasts = pd.read_sql("SELECT * FROM forecast_results", conn)
    forecasts["forecast_date"] = pd.to_datetime(forecasts["forecast_date"])

    conn.execute("DELETE FROM risk_alerts")
    as_of = datetime.now().date().isoformat()
    rows_inserted = 0

    for _, row in latest_stock.iterrows():
        sku_id = row["sku_id"]
        lead_weeks = max(1, round(row["lead_time_days"] / 7))
        sku_forecast = forecasts[forecasts["sku_id"] == sku_id].sort_values("forecast_date")
        demand_over_lead_time = sku_forecast["forecasted_units"].head(lead_weeks).sum()

        risk_type, risk_level = classify_risk(row["current_stock"], demand_over_lead_time, row["lead_time_days"])

        conn.execute(
            """INSERT INTO risk_alerts
               (sku_id, as_of_date, current_stock, forecasted_demand, risk_type, risk_level)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (sku_id, as_of, round(row["current_stock"], 1), round(demand_over_lead_time, 1),
             risk_type, risk_level)
        )
        rows_inserted += 1

    conn.commit()

    summary = pd.read_sql("SELECT risk_type, risk_level, COUNT(*) as n FROM risk_alerts GROUP BY risk_type, risk_level", conn)
    conn.close()

    print(f"Risk evaluated for {rows_inserted} SKUs.")
    print(summary.to_string(index=False))
    return summary


if __name__ == "__main__":
    run_risk_detection()
