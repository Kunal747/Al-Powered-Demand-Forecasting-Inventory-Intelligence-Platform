-- ============================================================
-- FORESIGHT - MySQL reference schema
-- ------------------------------------------------------------
-- The running project (database.py) uses SQLite so the whole
-- pipeline works out-of-the-box with zero setup for a demo or
-- submission. This file is the equivalent schema in MySQL, for
-- when/if you deploy FORESIGHT against a real MySQL server.
--
-- To switch: install mysql-connector-python, run this file
-- against your MySQL server, then change get_connection() in
-- src/database.py to return a mysql.connector connection using
-- the same table/column names used here. No other file needs
-- to change.
-- ============================================================

CREATE DATABASE IF NOT EXISTS foresight;
USE foresight;

CREATE TABLE IF NOT EXISTS sales_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    sku_id VARCHAR(20) NOT NULL,
    sku_name VARCHAR(100),
    category VARCHAR(50),
    region VARCHAR(50),
    units_sold DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    current_stock DECIMAL(10,2),
    reorder_level DECIMAL(10,2),
    lead_time_days INT,
    promotion_flag TINYINT(1),
    revenue DECIMAL(12,2),
    INDEX idx_sku_date (sku_id, date)
);

CREATE TABLE IF NOT EXISTS forecast_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_id VARCHAR(20) NOT NULL,
    forecast_date DATE NOT NULL,
    forecasted_units DECIMAL(10,2),
    model_used VARCHAR(50),
    mae DECIMAL(10,2),
    rmse DECIMAL(10,2),
    generated_at DATETIME,
    INDEX idx_sku_forecast (sku_id, forecast_date)
);

CREATE TABLE IF NOT EXISTS risk_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_id VARCHAR(20) NOT NULL,
    as_of_date DATE,
    current_stock DECIMAL(10,2),
    forecasted_demand DECIMAL(10,2),
    risk_type VARCHAR(20),
    risk_level VARCHAR(10),
    INDEX idx_sku_risk (sku_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_id VARCHAR(20) NOT NULL,
    as_of_date DATE,
    recommended_reorder_qty DECIMAL(10,2),
    safety_stock DECIMAL(10,2),
    reasoning TEXT,
    INDEX idx_sku_reco (sku_id)
);
