from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
st.set_page_config(page_title="SHIFTORA | Data Intelligence",page_icon="◈",layout="wide")
BG="#0B100E"; PANEL="#121B16"; LINE="rgba(190,215,197,.12)"; TEXT="#EEF3EF"; MUTED="#91A096"; GREEN="#A6D9B5"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{{background:{BG};color:{TEXT};font-family:'DM Sans',sans-serif}}
[data-testid="stSidebar"]{{background:#0E1511;border-right:1px solid {LINE}}}
.block-container{{max-width:1500px;padding-top:2rem;padding-bottom:3rem}}
h1,h2,h3{{font-family:Manrope,sans-serif;letter-spacing:-.04em;color:{TEXT}}}
[data-testid="stMetric"]{{background:linear-gradient(145deg,#17231B,{PANEL});border:1px solid {LINE};border-radius:15px;padding:17px 19px}}
[data-testid="stMetricLabel"]{{color:{MUTED}}}[data-testid="stMetricValue"]{{color:{TEXT};font-family:Manrope}}
.brand{{font:800 20px Manrope;letter-spacing:.12em;color:{TEXT};padding:8px 0 2px}}
.subbrand{{font-size:10px;letter-spacing:.18em;color:{GREEN};padding-bottom:22px}}
.kicker{{font-size:10px;letter-spacing:.18em;color:{GREEN};font-weight:700}}
.title{{font:750 34px Manrope;letter-spacing:-.05em;color:{TEXT};margin:4px 0}}
.subtitle{{color:{MUTED};font-size:13px;margin-bottom:20px}}
.cardtitle{{font:650 14px Manrope;color:{TEXT}}}.muted{{font-size:11px;color:{MUTED}}}
hr{{border-color:{LINE}}}
.stButton>button{{background:#1B3023;color:#E4F1E7;border:1px solid #355642;border-radius:9px}}
</style>
""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">◈ SHIFTORA</div><div class="subbrand">DATA INTELLIGENCE</div>',unsafe_allow_html=True)
    page=st.radio("Workspace",["Overview","Sales","Products","Marketing","Data Pipeline","Experiments"],label_visibility="visible")
    st.divider()
    st.caption("SHIFTORA v1.0 · Capstone edition")
    st.markdown("`●` System workspace")

path=OUT/"clean_orders.csv"
if not path.exists():
    st.error("Clean dataset not found. Run `python src/pipeline.py` from the project root.")
    st.stop()
df=pd.read_csv(path,parse_dates=["order_date"])
with st.container():
    a,b,c=st.columns([1.2,1,1])
    dmin,dmax=df.order_date.min().date(),df.order_date.max().date()
    with a: dates=st.date_input("Date range",(dmin,dmax),min_value=dmin,max_value=dmax)
    with b: cats=st.multiselect("Categories",sorted(df.category.unique()),default=sorted(df.category.unique()))
    with c: regs=st.multiselect("Regions",sorted(df.region.unique()),default=sorted(df.region.unique()))
if isinstance(dates,tuple) and len(dates)==2: start,end=dates
else: start,end=dmin,dmax
v=df[df.order_date.dt.date.between(start,end)&df.category.isin(cats)&df.region.isin(regs)].copy()
if v.empty:
    st.warning("No records match these filters."); st.stop()
def cash(x):
    return f"₹{x/1e6:.2f}M" if abs(x)>=1e6 else (f"₹{x/1e3:.1f}K" if abs(x)>=1e3 else f"₹{x:,.0f}")
def head(k,t,s):
    st.markdown(f'<div class="kicker">{k}</div><div class="title">{t}</div><div class="subtitle">{s}</div>',unsafe_allow_html=True)
def chart(fig,h=320):
    fig.update_layout(height=h,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color=MUTED),margin=dict(l=8,r=8,t=25,b=8),legend=dict(orientation="h",y=1.12),xaxis=dict(showgrid=False),yaxis=dict(gridcolor="rgba(190,215,197,.08)"))
    return st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
rev=v.revenue.sum(); n=len(v); aov=v.revenue.mean(); rr=v.is_returned.mean()*100
if page=="Overview":
    head("COMMAND CENTER","Sales overview","A focused view of business performance across your selected data.")
    st.caption("● SYNTHETIC SAMPLE DATA")
    x1,x2,x3,x4=st.columns(4)
    x1.metric("Total revenue",cash(rev));x2.metric("Orders analysed",f"{n:,}");x3.metric("Average order value",cash(aov));x4.metric("Return rate",f"{rr:.1f}%")
    l,r=st.columns([1.3,1])
    with l:
        st.markdown("**Revenue over time**")
        m=v.assign(month=v.order_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).revenue.sum()
        f=px.area(m,x="month",y="revenue");f.update_traces(line_color=GREEN,fillcolor="rgba(166,217,181,.12)");f.update_yaxes(tickprefix="₹",tickformat="~s");chart(f,330)
    with r:
        st.markdown("**Revenue mix by category**")
        q=v.groupby("category",as_index=False).revenue.sum()
        f=px.pie(q,names="category",values="revenue",hole=.68,color_discrete_sequence=["#A6D9B5","#7DAE91","#D6E7D9","#6D8F7B","#B7C9BC"]);chart(f,330)
    l,r=st.columns(2)
    with l:
        st.markdown("**Marketing channel performance**")
        q=v.groupby("marketing_channel",as_index=False).revenue.sum().sort_values("revenue")
        f=px.bar(q,x="revenue",y="marketing_channel",orientation="h",color_discrete_sequence=[GREEN]);f.update_layout(showlegend=False);f.update_xaxes(tickprefix="₹",tickformat="~s");chart(f,280)
    with r:
        st.markdown("**Revenue by region**")
        q=v.groupby("region",as_index=False).revenue.sum()
        f=px.bar(q,x="region",y="revenue",color_discrete_sequence=["#7DAE91"]);f.update_layout(showlegend=False);f.update_yaxes(tickprefix="₹",tickformat="~s");chart(f,280)
    st.markdown("**Latest transactions**")
    st.dataframe(v.sort_values("order_date",ascending=False).head(10),use_container_width=True,hide_index=True)
elif page=="Sales":
    head("PERFORMANCE","Sales analytics","Revenue movement, order volume and transaction-level detail.")
    a,b,c=st.columns(3);a.metric("Revenue",cash(rev));b.metric("Average order value",cash(aov));c.metric("Units sold",f"{v.quantity.sum():,}")
    m=v.assign(month=v.order_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(revenue=("revenue","sum"),orders=("order_id","count"))
    f=px.line(m,x="month",y="revenue",markers=True);f.update_traces(line_color=GREEN);f.update_yaxes(tickprefix="₹",tickformat="~s");chart(f,360)
    st.dataframe(v.sort_values("order_date",ascending=False),use_container_width=True,hide_index=True)
    st.download_button("Download filtered sales CSV",v.to_csv(index=False).encode(),"shiftora_sales.csv","text/csv")
elif page=="Products":
    head("CATALOG INTELLIGENCE","Product performance","Compare category revenue, units, pricing and returns.")
    q=v.groupby("category",as_index=False).agg(revenue=("revenue","sum"),orders=("order_id","count"),units=("quantity","sum"),avg_price=("unit_price","mean"),return_rate=("is_returned","mean"))
    l,r=st.columns(2)
    with l:
        f=px.bar(q.sort_values("revenue"),x="revenue",y="category",orientation="h",color_discrete_sequence=[GREEN]);f.update_layout(showlegend=False);f.update_xaxes(tickprefix="₹",tickformat="~s");chart(f,330)
    with r:
        f=px.bar(q,x="category",y="avg_price",color_discrete_sequence=["#7DAE91"]);f.update_layout(showlegend=False);f.update_yaxes(tickprefix="₹");chart(f,330)
    q["return_rate"]*=100
    st.dataframe(q.style.format({"revenue":"₹{:,.2f}","avg_price":"₹{:,.2f}","return_rate":"{:.1f}%"}),use_container_width=True,hide_index=True)
elif page=="Marketing":
    head("ACQUISITION INTELLIGENCE","Marketing performance","Understand which channels contribute to transaction revenue.")
    q=v.groupby("marketing_channel",as_index=False).agg(revenue=("revenue","sum"),orders=("order_id","count"),avg_order_value=("revenue","mean"),return_rate=("is_returned","mean"))
    q["return_rate"]*=100
    best=q.sort_values("revenue",ascending=False).iloc[0]
    a,b,c=st.columns(3);a.metric("Channels",q.marketing_channel.nunique());b.metric("Top channel",best.marketing_channel);c.metric("Top channel revenue",cash(best.revenue))
    f=px.bar(q.sort_values("revenue"),x="revenue",y="marketing_channel",orientation="h",color_discrete_sequence=[GREEN]);f.update_layout(showlegend=False);f.update_xaxes(tickprefix="₹",tickformat="~s");chart(f,350)
    st.dataframe(q.sort_values("revenue",ascending=False).style.format({"revenue":"₹{:,.2f}","avg_order_value":"₹{:,.2f}","return_rate":"{:.1f}%"}),use_container_width=True,hide_index=True)
elif page=="Data Pipeline":
    head("DATA OPERATIONS","Pipeline health","Review the data preparation stages and quality checks.")
    qp=OUT/"data_quality.json";q=json.loads(qp.read_text()) if qp.exists() else {}
    a,b,c=st.columns(3);a.metric("Raw records",f"{q.get('rows_before',len(df)):,}");b.metric("Clean records",f"{q.get('rows_after',len(df)):,}");c.metric("Missing after cleaning",f"{q.get('missing_values_after_cleaning',int(df.isna().sum().sum())):,}")
    for i,(name,desc) in enumerate([("Load source data","Read raw transactions and parse dates."),("Remove duplicates","Keep one record per unique order ID."),("Validate records","Filter invalid quantity and discount values."),("Handle missing values","Impute unit prices and fill missing regions."),("Engineer features","Create month, weekday and quarter features."),("Export ML-ready data","Save cleaned data and quality summary.")],1):
        st.markdown(f'<div style="background:{PANEL};border:1px solid {LINE};border-radius:12px;padding:15px;margin:8px 0"><span style="color:{GREEN};font-weight:700">0{i}</span>　<b>{name}</b><div style="color:{MUTED};font-size:12px;margin:5px 0 0 35px">{desc}</div></div>',unsafe_allow_html=True)
    st.json(q);st.dataframe(df.head(20),use_container_width=True,hide_index=True)
elif page=="Experiments":
    head("MODEL LAB","Experiments","Review baseline model evaluation on the held-out test dataset.")
    mp=OUT/"model_metrics.json";m=json.loads(mp.read_text()) if mp.exists() else {}
    a,b,c=st.columns(3);a.metric("Model",m.get("model","Not trained"));b.metric("Test records",f"{m.get('test_rows',0):,}");c.metric("R² score",f"{m.get('R2',0):.3f}")
    a,b,c=st.columns(3);a.metric("MAE",f"{m.get('MAE',0):,.2f}");b.metric("RMSE",f"{m.get('RMSE',0):,.2f}");c.metric("Random seed",m.get("random_state","—"))
    st.info("The dataset is synthetic. These model metrics are demonstration results, not evidence of production forecasting performance.")
    log=OUT/"experiment_log.csv"
    if log.exists(): st.dataframe(pd.read_csv(log),use_container_width=True,hide_index=True)
