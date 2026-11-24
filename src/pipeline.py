import json
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
MODELS = ROOT / "models"
OUT.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)

def load_and_clean(path=DATA / "raw_orders.csv"):
    df = pd.read_csv(path, parse_dates=["order_date"])
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    df = df[df["quantity"].between(1, 20)]
    df = df[df["discount_rate"].between(0, .80)]
    df["unit_price"] = df["unit_price"].fillna(df.groupby("category")["unit_price"].transform("median"))
    df["region"] = df["region"].fillna("Unknown")
    df["revenue"] = df["unit_price"] * df["quantity"] * (1 - df["discount_rate"])
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_dayofweek"] = df["order_date"].dt.dayofweek
    df["order_quarter"] = df["order_date"].dt.quarter
    quality = {
        "rows_before": int(initial_rows), "rows_after": int(len(df)),
        "duplicates_removed": int(initial_rows - len(pd.read_csv(path))),
        "rows_removed_by_rules": int(initial_rows - len(df)),
        "missing_values_after_cleaning": int(df.isna().sum().sum()),
        "validation": "Passed: positive quantity, discount between 0 and 0.80, revenue recalculated"
    }
    df.to_csv(OUT / "clean_orders.csv", index=False)
    (OUT / "data_quality.json").write_text(json.dumps(quality, indent=2))
    return df, quality

def train_model(df):
    # Estimate order revenue from order attributes; order_id/customer_id excluded to avoid leakage/high cardinality.
    features = ["category","quantity","discount_rate","marketing_channel","region",
                "payment_method","order_dayofweek","order_quarter"]
    target = "revenue"
    X, y = df[features], df[target]
    categorical = ["category","marketing_channel","region","payment_method"]
    numeric = [c for c in features if c not in categorical]
    prep = ColumnTransformer([
        ("num", Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]), categorical)
    ])
    model = RandomForestRegressor(n_estimators=250, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1)
    pipe = Pipeline([("preprocess",prep),("model",model)])
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=.2,random_state=42)
    pipe.fit(X_train,y_train)
    pred = pipe.predict(X_test)
    metrics = {
        "model":"RandomForestRegressor",
        "test_rows":int(len(y_test)),
        "MAE":float(mean_absolute_error(y_test,pred)),
        "RMSE":float(mean_squared_error(y_test,pred)**.5),
        "R2":float(r2_score(y_test,pred)),
        "random_state":42
    }
    import json
    (OUT/"model_metrics.json").write_text(json.dumps(metrics,indent=2))
    joblib.dump(pipe, MODELS/"revenue_pipeline.joblib")
    return metrics

if __name__ == "__main__":
    data, quality = load_and_clean()
    metrics = train_model(data)
    print("Data quality:", quality)
    print("Model metrics:", metrics)
