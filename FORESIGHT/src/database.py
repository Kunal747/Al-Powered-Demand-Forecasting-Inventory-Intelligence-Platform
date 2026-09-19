# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "foresight.db")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "foresight_sales_inventory_clean.csv")

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
    risk_type TEXT,
    risk_level TEXT
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
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Always ensure schema exists
    conn.executescript(SCHEMA)
    conn.commit()
    
    # Check if sales_history has data, if not load or insert dummy row to prevent crashes
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_history;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        csv_path = CLEAN_CSV
        if not os.path.exists(csv_path):
            csv_path = "data/foresight_sales_inventory_clean.csv"
            
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                df = df.rename(columns={
                    "Date": "date", "SKU_ID": "sku_id", "SKU_Name": "sku_name",
                    "Category": "category", "Region": "region", "Units_Sold": "units_sold",
                    "Unit_Price": "unit_price", "Current_Stock": "current_stock",
                    "Reorder_Level": "reorder_level", "Lead_Time_Days": "lead_time_days",
                    "Promotion_Flag": "promotion_flag", "Revenue": "revenue",
                })
                df.to_sql("sales_history", conn, if_exists="append", index=False)
                conn.commit()
            except Exception as e:
                print(f"Error loading CSV: {e}")
        
    return conn

if __name__ == "__main__":
    conn = get_connection()
    conn.close()
    print("Database initialized successfully.")