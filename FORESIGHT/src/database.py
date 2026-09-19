# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "foresight.db")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "foresight_sales_inventory_clean.csv")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create all tables if not exist
    cursor.executescript("""
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
    """)
    conn.commit()
    
    # 2. Check if sales_history is empty, if yes, load CSV or insert fallback data
    cursor.execute("SELECT COUNT(*) FROM sales_history;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        csv_paths = [
            CLEAN_CSV,
            "data/foresight_sales_inventory_clean.csv",
            "../data/foresight_sales_inventory_clean.csv"
        ]
        loaded = False
        for path in csv_paths:
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    df = df.rename(columns={
                        "Date": "date", "SKU_ID": "sku_id", "SKU_Name": "sku_name",
                        "Category": "category", "Region": "region", "Units_Sold": "units_sold",
                        "Unit_Price": "unit_price", "Current_Stock": "current_stock",
                        "Reorder_Level": "reorder_level", "Lead_Time_Days": "lead_time_days",
                        "Promotion_Flag": "promotion_flag", "Revenue": "revenue",
                    })
                    df.to_sql("sales_history", conn, if_exists="append", index=False)
                    conn.commit()
                    loaded = True
                    break
                except Exception as e:
                    print(f"Error loading {path}: {e}")
        
        # If CSV not found anywhere, insert sample data so dashboard works instantly
        if not loaded:
            cursor.execute("""
            INSERT INTO sales_history (date, sku_id, sku_name, category, region, units_sold, unit_price, current_stock, reorder_level, lead_time_days, promotion_flag, revenue)
            VALUES ('2026-01-01', 'SKU_DEMO_01', 'Demo Product', 'General', 'North', 100, 50.0, 200, 50, 5, 0, 5000.0);
            """)
            cursor.execute("""
            INSERT INTO forecast_results (sku_id, forecast_date, forecasted_units, model_used, mae, rmse, generated_at)
            VALUES ('SKU_DEMO_01', '2026-01-08', 120, 'Prophet', 2.5, 3.1, '2026-01-01');
            """)
            cursor.execute("""
            INSERT INTO risk_alerts (sku_id, as_of_date, current_stock, forecasted_demand, risk_type, risk_level)
            VALUES ('SKU_DEMO_01', '2026-01-01', 200, 120, 'Normal', 'Low');
            """)
            cursor.execute("""
            INSERT INTO recommendations (sku_id, as_of_date, recommended_reorder_qty, safety_stock, reasoning)
            VALUES ('SKU_DEMO_01', '2026-01-01', 0, 30, 'Stock levels are optimal.');
            """)
            conn.commit()
            
    return conn

if __name__ == "__main__":
    conn = get_connection()
    conn.close()
    print("Database ready.")