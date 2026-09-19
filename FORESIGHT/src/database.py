# -*- coding: utf-8 -*-
"""
database.py
------------
WHAT: Creates the FORESIGHT database schema and loads cleaned data into it.
WHY : A relational database keeps sales history, inventory, forecasts, risk
      alerts and recommendations in one queryable place instead of loose
      CSV files, and is what the Streamlit dashboard reads from.
HOW : Uses Python's built-in `sqlite3` so the whole project runs anywhere
      with zero external setup (no server, no credentials).
"""
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "foresight.db")
CLEAN_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "foresight_sales_inventory_clean.csv")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    sku_id TEXT NOT NULL,
    sku_name TEXT,
    category TEXT,
    region TEXT,
    units_sold REAL,
    unit_price REAL,
    current_stock REAL,
    reorder_level REAL,
    lead_time_days INTEGER,
    promotion_flag INTEGER,
    revenue REAL
);

CREATE TABLE IF NOT EXISTS forecast_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_id TEXT NOT NULL,
    forecast_date TEXT NOT NULL,
    forecasted_units REAL,
    model_used TEXT,
    mae REAL,
    rmse REAL,
    generated_at TEXT
);

CREATE TABLE IF NOT EXISTS risk_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_id TEXT NOT NULL,
    as_of_date TEXT,
    current_stock REAL,
    forecasted_demand REAL,
    risk_type TEXT,        -- 'Stockout', 'Overstock', or 'Normal'
    risk_level TEXT        -- 'High', 'Medium', 'Low'
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_id TEXT NOT NULL,
    as_of_date TEXT,
    recommended_reorder_qty REAL,
    safety_stock REAL,
    reasoning TEXT
);
"""


def get_connection():
    """Returns a DB connection and auto-initializes tables/data if missing (great for cloud deployment)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Check if tables exist, if not initialize schema and load data automatically
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales_history';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        conn.executescript(SCHEMA)
        conn.commit()
        _load_initial_data(conn)
    else:
        cursor.execute("SELECT COUNT(*) FROM sales_history;")
        count = cursor.fetchone()[0]
        if count == 0:
            _load_initial_data(conn)
            
    return conn


def _load_initial_data(conn):
    if os.path.exists(CLEAN_CSV):
        df = pd.read_csv(CLEAN_CSV)
        df = df.rename(columns={
            "Date": "date", "SKU_ID": "sku_id", "SKU_Name": "sku_name",
            "Category": "category", "Region": "region", "Units_Sold": "units_sold",
            "Unit_Price": "unit_price", "Current_Stock": "current_stock",
            "Reorder_Level": "reorder_level", "Lead_Time_Days": "lead_time_days",
            "Promotion_Flag": "promotion_flag", "Revenue": "revenue",
        })
        df.to_sql("sales_history", conn, if_exists="append", index=False)
        conn.commit()
        print("Initial sales history loaded automatically.")


def init_schema():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("Schema created (or already existed).")


def load_sales_history(csv_path: str = CLEAN_CSV):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "Date": "date", "SKU_ID": "sku_id", "SKU_Name": "sku_name",
        "Category": "category", "Region": "region", "Units_Sold": "units_sold",
        "Unit_Price": "unit_price", "Current_Stock": "current_stock",
        "Reorder_Level": "reorder_level", "Lead_Time_Days": "lead_time_days",
        "Promotion_Flag": "promotion_flag", "Revenue": "revenue",
    })
    conn = get_connection()
    conn.execute("DELETE FROM sales_history")
    df.to_sql("sales_history", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"Loaded {len(df)} rows into sales_history.")


if __name__ == "__main__":
    init_schema()
    load_sales_history()