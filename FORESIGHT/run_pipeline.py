# -*- coding: utf-8 -*-
"""
run_pipeline.py
-----------------
WHAT: Runs the entire FORESIGHT pipeline end-to-end in the correct order.
WHY : So the whole project can be reproduced with a single command --
      important for a demo/submission where you need everything to run
      without manually calling five separate scripts in the right order.
HOW : Imports and calls each stage's function directly (no subprocess calls),
      so a failure in one stage raises a clear Python traceback instead of
      silently failing in a shell script.

Run: python run_pipeline.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_cleaning import clean_dataset, CLEAN_PATH
from database import init_schema, load_sales_history
from forecasting import run_forecasting_pipeline
from risk_detection import run_risk_detection
from recommendation import run_recommendation_engine


def main():
    print("=" * 60)
    print("STEP 1/5: Cleaning raw data")
    print("=" * 60)
    cleaned = clean_dataset()
    cleaned.to_csv(CLEAN_PATH, index=False)

    print("\n" + "=" * 60)
    print("STEP 2/5: Setting up database & loading data")
    print("=" * 60)
    init_schema()
    load_sales_history()

    print("\n" + "=" * 60)
    print("STEP 3/5: Running demand forecasting")
    print("=" * 60)
    run_forecasting_pipeline()

    print("\n" + "=" * 60)
    print("STEP 4/5: Detecting stockout/overstock risk")
    print("=" * 60)
    run_risk_detection()

    print("\n" + "=" * 60)
    print("STEP 5/5: Generating reorder recommendations")
    print("=" * 60)
    run_recommendation_engine()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE. Run the dashboard with:")
    print("   streamlit run dashboard/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
