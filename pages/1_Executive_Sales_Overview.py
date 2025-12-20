import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import plotly.express as px
from millify import millify


# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(layout="wide")

col_logo, col_title = st.columns([1,3])

with col_logo:
    st.image('Resources/logo.jpeg', width=200)

with col_title:
    st.title("🏆 Executive Sales Overview Dashboard")


# ------------------------------------------
# LOAD DATA
# ------------------------------------------
# importing data
sales_pipeline = pd.read_csv('Resources/sales_pipeline.csv')
sales_pipeline['close_date'] =  pd.to_datetime(sales_pipeline['close_date'],format = '%d-%m-%Y',errors="coerce")
sales_pipeline['engage_date'] = pd.to_datetime(sales_pipeline['engage_date'],format = '%Y-%m-%d',errors="coerce")
accounts = pd.read_csv('Resources/accounts.csv')

# merge region + sector + other fields
df = sales_pipeline.merge(accounts, on="account", how="inner")

# month fields
df["month_num"] = df["close_date"].dt.month
df["month_name"] = df["close_date"].dt.month_name()

# ------------------------------------------
# SLICERS
# ------------------------------------------
with st.sidebar:
    st.header("🔍 Filters")

    # month slicer
    month_list = (
        df[["month_num","month_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("month_num")["month_name"]
        .tolist()
    )
    selected_months = st.multiselect("Select Month", month_list)

    if not selected_months:
        selected_months = month_list

    # OPEN PIPELINE DATAFRAME
    open_df = df[df['deal_stage'].isin(['Prospecting','Engaging'])]

    # month name for open deals uses engage_date instead of close_date
    open_df['month_num'] = open_df['engage_date'].dt.month
    open_df['month_name'] = open_df['engage_date'].dt.month_name()


    # product slicer
    prod_list = sorted(df["product"].dropna().unique())
    selected_products = st.multiselect("Select Product", prod_list)

    if not selected_products:
        selected_products = prod_list

    # region slicer
    region_list = sorted(df["office_location"].dropna().unique())
    selected_regions = st.multiselect("Select Region", region_list)

    if not selected_regions:
        selected_regions = region_list

# ------------------------------------------
# APPLY FILTERS
# ------------------------------------------
filtered = df.copy()


filtered = filtered[
    (filtered["month_name"].isin(selected_months)) |
    (filtered["deal_stage"].isin(["Prospecting","Engaging"]))
]

filtered = filtered[
    (filtered["product"].isin(selected_products)) |
    (filtered["deal_stage"].isin(["Prospecting","Engaging"]))
]

filtered = filtered[
    (filtered["office_location"].isin(selected_regions)) |
    (filtered["deal_stage"].isin(["Prospecting","Engaging"]))
]



open_filtered = open_df.copy()

open_filtered = open_filtered[open_filtered["product"].isin(selected_products)]
open_filtered = open_filtered[open_filtered["office_location"].isin(selected_regions)]

# ------------------------------------------
# KPIs
# ------------------------------------------
Total_Revenue = df['close_value'].sum()
Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)

total_opps = filtered["opportunity_id"].nunique()
won_opps = filtered[filtered["deal_stage"]=="Won"]["opportunity_id"].nunique()
lost_opps = filtered[filtered["deal_stage"]=="Lost"]["opportunity_id"].nunique()
open_opps = len(open_filtered)
win_rate = (won_opps / total_opps * 100) if total_opps > 0 else 0
avg_deal_value = filtered.loc[filtered["deal_stage"]=="Won","close_value"].mean()
avg_sales_cycle = (filtered["close_date"] - filtered["engage_date"]).dt.days.mean()
active_customers = accounts["account"].nunique()

# ------------------------------------------
# KPI UI
# ------------------------------------------
k1,k2,k3 = st.columns(3)
k4,k5,k6 = st.columns(3)
k7,k8,k9 = st.columns(3)

k1.metric("💰 Total Revenue", Total_Revenue_Display)
k2.metric("📁 Total Opps", f"{total_opps:,}")
k3.metric("🏆 Won Opps", f"{won_opps:,}")

k4.metric("📂 Open Opps", f"{open_opps:,}")
k5.metric("❌ Lost Opps", f"{lost_opps:,}")
k6.metric("📈 Win Rate %", f"{win_rate:.2f}%")

k7.metric("💵 Avg Deal Value", f"${avg_deal_value:,.0f}")
k8.metric("👥 Active Customers", f"{active_customers:,}")
k9.metric("⏱ Avg Sales Cycle", f"{avg_sales_cycle:.0f} days")

# ------------------------------------------
# VISUALS
# ------------------------------------------
# monthly trend
monthly = (
    filtered.groupby(["month_num","month_name"])["close_value"]
    .sum()
    .reset_index()
    .sort_values("month_num")
)
st.subheader("📈 Monthly Revenue Trend")
st.plotly_chart(px.line(monthly, x="month_name", y="close_value", markers=True), use_container_width=False)

# funnel
stage = (
    filtered.groupby("deal_stage")["opportunity_id"]
    .count()
    .reset_index()
)

# correct CRM stage order
order = ["Prospecting", "Engaging", "Lost", "Won"]
stage["deal_stage"] = pd.Categorical(stage["deal_stage"], categories=order, ordered=True)
stage = stage.sort_values("deal_stage")


st.subheader("🔻 Opportunity Stage Distribution Funnel")
# reverse funnel direction
fig = px.funnel(
    stage,
    y="deal_stage",
    x="opportunity_id",
    title="Opportunity Funnel",
)

# make Power BI look
fig.update_traces(
    marker={"color": ["#4B77BE", "#5DADE2", "#F5B041", "#27AE60"]}  # optional colors
)

st.plotly_chart(fig, use_container_width=True)


# revenue by product
prod = (
    filtered.groupby("product")["close_value"]
    .sum()
    .reset_index().sort_values('close_value')
)
st.subheader("📦 Revenue by Product")
st.plotly_chart(px.bar(prod, x="product", y="close_value"), use_container_width=False)

# revenue by Sector
sect = (filtered.groupby('sector')['close_value'].sum()
        .reset_index().sort_values('close_value',ascending = True)
       )
st.subheader("📂 Revenue Contribution by Sector")
st.plotly_chart(px.bar(sect,x='close_value',y='sector',orientation = 'h'))

# revenue by region
region = (
    filtered.groupby("office_location")["close_value"]
    .sum()
    .reset_index()
)
st.subheader("🌍 Revenue by Region")
st.plotly_chart(px.bar(region, x="office_location", y="close_value"), use_container_width=False)

# top accounts
acc = (
    filtered.groupby("account")["close_value"]
    .sum()
    .reset_index()
    .sort_values("close_value", ascending=False)
    .head(10).sort_values("close_value",ascending = True)
)
st.subheader("🏢 Top Accounts by Revenue")
st.plotly_chart(px.bar(acc, x="close_value", y="account", orientation="h"), use_container_width=False)

# raw table
st.subheader("📄 Raw Data")
st.dataframe(filtered)
