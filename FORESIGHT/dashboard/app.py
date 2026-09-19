@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS sales_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, sku_id TEXT NOT NULL, sku_name TEXT,
        category TEXT, region TEXT, units_sold REAL, unit_price REAL,
        current_stock REAL, reorder_level REAL, lead_time_days INTEGER,
        promotion_flag INTEGER, revenue REAL
    );
    CREATE TABLE IF NOT EXISTS forecast_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id TEXT NOT NULL, forecast_date TEXT NOT NULL,
        forecasted_units REAL, model_used TEXT, mae REAL, rmse REAL, generated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS risk_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id TEXT NOT NULL, as_of_date TEXT, current_stock REAL,
        forecasted_demand REAL, risk_type TEXT, risk_level TEXT
    );
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id TEXT NOT NULL, as_of_date TEXT, recommended_reorder_qty REAL,
        safety_stock REAL, reasoning TEXT
    );
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM sales_history;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        csv_paths = [
            os.path.join(os.path.dirname(__file__), "..", "data", "foresight_sales_inventory_clean.csv"),
            "data/foresight_sales_inventory_clean.csv",
            "foresight_sales_inventory_clean.csv"
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
                except Exception:
                    pass
        
        # Fallback sample data if CSV is completely missing
        if not loaded:
            cursor.execute("INSERT INTO sales_history (date, sku_id, sku_name, category, region, units_sold, unit_price, current_stock, reorder_level, lead_time_days, promotion_flag, revenue) VALUES ('2026-01-01', 'SKU_001', 'Sample Product A', 'Electronics', 'North', 120, 45.0, 150, 40, 5, 0, 5400.0);")
            cursor.execute("INSERT INTO sales_history (date, sku_id, sku_name, category, region, units_sold, unit_price, current_stock, reorder_level, lead_time_days, promotion_flag, revenue) VALUES ('2026-01-02', 'SKU_002', 'Sample Product B', 'Apparel', 'South', 85, 30.0, 30, 50, 4, 1, 2550.0);")
            
            cursor.execute("INSERT INTO forecast_results (sku_id, forecast_date, forecasted_units, model_used, mae, rmse, generated_at) VALUES ('SKU_001', '2026-01-08', 130, 'Prophet', 2.1, 3.4, '2026-01-01');")
            cursor.execute("INSERT INTO forecast_results (sku_id, forecast_date, forecasted_units, model_used, mae, rmse, generated_at) VALUES ('SKU_002', '2026-01-08', 90, 'Prophet', 1.8, 2.5, '2026-01-01');")
            
            cursor.execute("INSERT INTO risk_alerts (sku_id, as_of_date, current_stock, forecasted_demand, risk_type, risk_level) VALUES ('SKU_001', '2026-01-01', 150, 130, 'Normal', 'Low');")
            cursor.execute("INSERT INTO risk_alerts (sku_id, as_of_date, current_stock, forecasted_demand, risk_type, risk_level) VALUES ('SKU_002', '2026-01-01', 30, 90, 'Stockout', 'High');")
            
            cursor.execute("INSERT INTO recommendations (sku_id, as_of_date, recommended_reorder_qty, safety_stock, reasoning) VALUES ('SKU_001', '2026-01-01', 0, 40, 'Stock is sufficient.');")
            cursor.execute("INSERT INTO recommendations (sku_id, as_of_date, recommended_reorder_qty, safety_stock, reasoning) VALUES ('SKU_002', '2026-01-01', 100, 35, 'Predicted stockout within lead time.');")
            conn.commit()

    sales = pd.read_sql("SELECT * FROM sales_history", conn)
    forecast = pd.read_sql("SELECT * FROM forecast_results", conn)
    risk = pd.read_sql("SELECT * FROM risk_alerts", conn)
    reco = pd.read_sql("SELECT * FROM recommendations", conn)
    conn.close()
    
    if not sales.empty and "date" in sales.columns:
        sales["date"] = pd.to_datetime(sales["date"])
    if not forecast.empty and "forecast_date" in forecast.columns:
        forecast["forecast_date"] = pd.to_datetime(forecast["forecast_date"])
        
    return sales, forecast, risk, reco