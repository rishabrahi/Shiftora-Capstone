from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"outputs"/"clean_orders.csv",parse_dates=["order_date"])
(ROOT/"outputs"/"figures").mkdir(parents=True,exist_ok=True)
monthly=df.groupby(df.order_date.dt.to_period("M").astype(str)).revenue.sum()
monthly.plot(marker="o",title="Monthly Revenue Trend",ylabel="Revenue (INR)",figsize=(9,4)); plt.xticks(rotation=60); plt.tight_layout()
plt.savefig(ROOT/"outputs"/"figures"/"monthly_revenue.png",dpi=150); plt.close()
for col in ["category","marketing_channel","region"]:
    df.groupby(col).revenue.sum().sort_values().plot(kind="barh",title=f"Revenue by {col}",figsize=(8,4))
    plt.xlabel("Revenue (INR)"); plt.tight_layout()
    plt.savefig(ROOT/"outputs"/"figures"/f"{col}_revenue.png",dpi=150); plt.close()
print(df.describe(include="all").to_string())
