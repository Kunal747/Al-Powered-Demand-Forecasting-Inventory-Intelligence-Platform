# -*- coding: utf-8 -*-
"""
forecasting.py
---------------
WHAT: Trains a demand forecasting model per SKU and stores the next 8 weeks
      of predicted demand into the forecast_results table.
WHY : Knowing *future* demand (not just past sales) is what lets the risk
      and recommendation modules act ahead of a stockout instead of reacting
      after it happens.
HOW : Primary model = ARIMA (statsmodels) -- a standard, explainable
      time-series model, well suited to weekly sales with trend + seasonality.
      Fallback model = Weighted Moving Average -- if ARIMA fails to converge
      for a particular SKU (can happen on short/irregular series), we fall
      back automatically so the pipeline NEVER crashes on a single bad SKU.
      Accuracy is measured with MAE and RMSE on a held-out validation window.

Run directly: python src/forecasting.py
"""
import warnings
warnings.filterwarnings("ignore")  # statsmodels convergence warnings are expected & handled

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA

from database import get_connection

FORECAST_HORIZON_WEEKS = 8
VALIDATION_WEEKS = 8


def mae_rmse(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    return round(mae, 2), round(rmse, 2)


def weighted_moving_average_forecast(series: pd.Series, horizon: int, window: int = 6):
    """Simple, robust fallback: weighted average of the last `window` points,
    weights favour recent weeks. Used only if ARIMA fails for a SKU."""
    recent = series.tail(window).values
    weights = np.arange(1, len(recent) + 1)
    avg = np.average(recent, weights=weights)
    return np.repeat(avg, horizon)


def forecast_sku(series: pd.Series, horizon: int = FORECAST_HORIZON_WEEKS):
    """
    Returns (forecast_values, model_name, mae, rmse).
    Tries ARIMA(1,1,1) first; validates on the last VALIDATION_WEEKS.
    Falls back to weighted moving average on any failure.
    """
    train = series.iloc[:-VALIDATION_WEEKS]
    valid = series.iloc[-VALIDATION_WEEKS:]

    try:
        model = ARIMA(train.values, order=(1, 1, 1))
        fitted = model.fit()
        valid_pred = fitted.forecast(steps=VALIDATION_WEEKS)
        mae, rmse = mae_rmse(valid.values, valid_pred)

        # Refit on the FULL series for the actual future forecast
        full_model = ARIMA(series.values, order=(1, 1, 1))
        full_fitted = full_model.fit()
        forecast_values = full_fitted.forecast(steps=horizon)
        forecast_values = np.clip(forecast_values, 0, None)  # demand can't be negative
        return forecast_values, "ARIMA(1,1,1)", mae, rmse

    except Exception:
        # Fallback path -- validate the fallback the same way for a fair MAE/RMSE
        valid_pred = weighted_moving_average_forecast(train, VALIDATION_WEEKS)
        mae, rmse = mae_rmse(valid.values, valid_pred)
        forecast_values = weighted_moving_average_forecast(series, horizon)
        return forecast_values, "WeightedMovingAverage", mae, rmse


def run_forecasting_pipeline():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM sales_history ORDER BY sku_id, date", conn)
    df["date"] = pd.to_datetime(df["date"])

    conn.execute("DELETE FROM forecast_results")

    results_summary = []
    generated_at = datetime.now().isoformat(timespec="seconds")

    for sku_id, group in df.groupby("sku_id"):
        series = group.set_index("date")["units_sold"].asfreq("W-SUN")
        series = series.interpolate()  # fill any calendar gaps from asfreq

        forecast_values, model_used, mae, rmse = forecast_sku(series)

        last_date = series.index.max()
        for i, val in enumerate(forecast_values, start=1):
            f_date = (last_date + timedelta(weeks=i)).date().isoformat()
            conn.execute(
                """INSERT INTO forecast_results
                   (sku_id, forecast_date, forecasted_units, model_used, mae, rmse, generated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sku_id, f_date, round(float(val), 1), model_used, mae, rmse, generated_at)
            )
        results_summary.append({"sku_id": sku_id, "model": model_used, "mae": mae, "rmse": rmse})

    conn.commit()
    conn.close()

    summary_df = pd.DataFrame(results_summary)
    print(f"Forecasted {len(summary_df)} SKUs for {FORECAST_HORIZON_WEEKS} weeks ahead.")
    print(summary_df["model"].value_counts().to_string())
    print(f"\nAverage MAE across SKUs: {summary_df['mae'].mean():.2f}")
    print(f"Average RMSE across SKUs: {summary_df['rmse'].mean():.2f}")
    return summary_df


if __name__ == "__main__":
    run_forecasting_pipeline()
