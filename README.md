# Shiftora — E-commerce Sales Analytics & ML-Ready Data Workflow

## Project overview
Shiftora is a reproducible data-engineering and analytics workflow built around a sample e-commerce transaction dataset. It demonstrates data acquisition, cleaning, validation, exploratory data analysis, visualisation, feature engineering, reusable preprocessing and experiment evaluation.

> Dataset note: `data/raw_orders.csv` is a **synthetic sample dataset generated for this academic project**. It is not real customer or business data.

## Repository structure
- `data/raw_orders.csv` — source sample transactions
- `src/pipeline.py` — cleaning, validation, preprocessing and model training
- `src/eda.py` — reusable exploratory charts
- `outputs/clean_orders.csv` — cleaned ML-ready data (generated)
- `outputs/data_quality.json` — data quality checks (generated)
- `outputs/model_metrics.json` — held-out model metrics (generated)
- `outputs/figures/` — exported visualisations
- `models/revenue_pipeline.joblib` — fitted preprocessing + model pipeline (generated)
- `app.py` — interactive Streamlit dashboard
- `report/` — capstone report

## Run locally
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the pipeline: `python src/pipeline.py`
5. Generate EDA figures: `python src/eda.py`
6. Launch dashboard: `streamlit run app.py`

## Workflow
1. Acquire the sample CSV.
2. Remove duplicate order IDs and invalid quantity/discount rows.
3. Impute missing unit prices using category medians; label missing regions as `Unknown`.
4. Recalculate revenue from price, quantity and discount.
5. Derive month, day-of-week and quarter features.
6. Explore trends by month, category and marketing channel.
7. Build a reusable scikit-learn preprocessing + Random Forest pipeline.
8. Evaluate on a held-out 20% test split using MAE, RMSE and R².

## Limitations
- Data is synthetic and does not represent an actual retailer.
- Revenue is mathematically derived from price, quantity and discount; the model is a demonstration of an ML-ready pipeline, not a production forecasting system.
- Model scores depend on the generated sample and should not be interpreted as real-world business performance.\n