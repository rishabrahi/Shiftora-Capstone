import streamlit as st
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parent
clean_path=ROOT/"outputs"/"clean_orders.csv"
st.set_page_config(page_title="Shiftora | Sales Analytics",layout="wide")
st.title("Shiftora — E-commerce Sales Analytics")
st.caption("Data engineering • EDA • Feature engineering • ML-ready preprocessing")
if not clean_path.exists():
    st.warning("Run the pipeline first: python src/pipeline.py")
    st.stop()
df=pd.read_csv(clean_path,parse_dates=["order_date"])
c1,c2,c3,c4=st.columns(4)
c1.metric("Total Revenue",f"₹{df.revenue.sum():,.0f}")
c2.metric("Orders",f"{len(df):,}")
c3.metric("Average Order Value",f"₹{df.revenue.mean():,.0f}")
c4.metric("Return Rate",f"{df.is_returned.mean()*100:.1f}%")
st.subheader("Filters")
cats=st.multiselect("Category",sorted(df.category.unique()),default=sorted(df.category.unique()))
regions=st.multiselect("Region",sorted(df.region.unique()),default=sorted(df.region.unique()))
view=df[df.category.isin(cats)&df.region.isin(regions)]
left,right=st.columns(2)
with left:
    st.subheader("Revenue by month")
    monthly=view.groupby(view.order_date.dt.to_period("M").astype(str)).revenue.sum()
    st.line_chart(monthly)
with right:
    st.subheader("Revenue by category")
    st.bar_chart(view.groupby("category").revenue.sum())
st.subheader("Marketing channel performance")
st.bar_chart(view.groupby("marketing_channel").revenue.sum())
st.subheader("Cleaned transaction sample")
st.dataframe(view.head(100),use_container_width=True)
st.download_button("Download filtered CSV",view.to_csv(index=False).encode(), "filtered_orders.csv","text/csv")\n