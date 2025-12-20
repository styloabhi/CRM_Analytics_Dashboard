# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_jupyter import StreamlitPatcher
StreamlitPatcher().jupyter()
import streamlit as st
from millify import millify


# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(
    page_title="Account 360 Dashboard",
    page_icon="🏢",
    layout='wide'
)


# ----------------------------
# SIDEBAR THEME STYLE
# ----------------------------
st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #08142c, #0a182f, #0d1e3b);
    color: white;
    padding: 20px;
}

[data-testid="stSidebar"] * {
    color: white !important;
    font-size: 15px;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
}

.sidebar-label {
    font-size: 16px;
    font-weight: 600;
    color: #9db7d6 !important;
    margin-top: 18px;
    margin-bottom: 5px;
}

div[data-baseweb="select"] > div {
    background-color: #132240 !important;
    border-radius: 10px !important;
    border: 1px solid #3c4f70 !important;
    color: white !important;
}

span[data-baseweb="tag"] {
    background-color: #5e82ff !important;
    color: white !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ----------------------------
# KPI CARD STYLE
# ----------------------------
st.markdown("""
<style>
.kpi-box {
    background: rgba(255,255,255,0.20);
    backdrop-filter: blur(8px);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.3);
}
.kpi-title {
    font-size: 18px;
    font-weight: 600;
    color:#2A3E5C;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color:#1A2A40;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# HEADER
# ----------------------------
col_logo, col_title = st.columns([1,4])

with col_logo:
    st.image('Resources/logo.jpeg', width=140)

with col_title:
    st.markdown(
        """
        <h1 style='font-size:48px; font-weight:900; margin-bottom:0; color:#1A2A40;'>
            🏢 Account 360 Dashboard
        </h1>
        <p style='font-size:20px; color:#5a6a81; font-weight:500;'>
            Account performance overview across revenue, sector, region & opportunities.
        </p>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# LOAD DATA
# ----------------------------
account360 = pd.read_csv("Resources/account_360.csv")
account360['first_engage_date'] = pd.to_datetime(account360['first_engage_date'], format='%d-%m-%Y')
account360['last_close_date'] = pd.to_datetime(account360['last_close_date'], format='%d-%m-%Y')

account360['month_num'] = account360['first_engage_date'].dt.month
account360['month_name'] = account360['first_engage_date'].dt.month_name()


# ----------------------------
# CREATE SLICER LISTS
# ----------------------------
month_list = (
    account360[['month_num','month_name']]
    .dropna()
    .drop_duplicates()
    .sort_values("month_num")["month_name"]
    .tolist()
)

account_list = sorted(account360['account'].dropna().unique())
sector_list = sorted(account360['sector'].dropna().unique())


# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
with st.sidebar:

    st.image("Resources/logo.jpeg", width=140)

    st.markdown("<div class='sidebar-title'>📊 FILTER PANEL</div>", unsafe_allow_html=True)

    # ------------------ MONTH SLICER ------------------
    st.markdown("<div class='sidebar-label'>📅 Select Month</div>", unsafe_allow_html=True)
    selected_months = st.multiselect("Select Month", month_list)
    if not selected_months:
        selected_months = month_list

    # ------------------ ACCOUNT SLICER ------------------
    st.markdown("<div class='sidebar-label'>🏢 Select Account</div>", unsafe_allow_html=True)
    selected_account = st.multiselect("Select Account", account_list)
    if not selected_account:
        selected_account = account_list

    # ------------------ SECTOR SLICER ------------------
    st.markdown("<div class='sidebar-label'>🧩 Select Sector</div>", unsafe_allow_html=True)
    selected_sector = st.multiselect("Select Sector", sector_list)
    if not selected_sector:
        selected_sector = sector_list


# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered = account360[
    account360["month_name"].isin(selected_months) &
    account360["sector"].isin(selected_sector) &
    account360["account"].isin(selected_account)
]


# ----------------------------
# KPI VALUES
# ----------------------------
Total_Revenue = account360['revenue_won'].sum()
Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)

Total_Opportunities = filtered['total_opportunities'].sum()
Open_Opportunities = filtered['open_opportunities'].sum()
Won_Opportunities = filtered['won_opportunities'].sum()
Lost_Opportunities = filtered['lost_opportunities'].sum()

Win_Rate = (Won_Opportunities / Total_Opportunities * 100) if Total_Opportunities > 0 else 0

Product_sold = filtered['distinct_products_sold'].sum()
Active_Customers = len(filtered)
avg_deal_value = filtered['avg_win_deal_value'].mean()


# ----------------------------
# KPI CARD FUNCTION
# ----------------------------
def kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# KPI DISPLAY GRID
# ----------------------------
k1, k2, k3 = st.columns(3)
with k1: kpi_card("💰 Total Revenue", Total_Revenue_Display)
with k2: kpi_card("📁 Total Opportunities", millify(Total_Opportunities, 2))
with k3: kpi_card("📂 Open Opportunities", millify(Open_Opportunities, 2))

k4, k5, k6 = st.columns(3)
with k4: kpi_card("🏆 Win Rate", f"{Win_Rate:.2f}%")
with k5: kpi_card("❌ Lost Opportunities", millify(Lost_Opportunities, 2))
with k6: kpi_card("📦 Total Products Sold", millify(Product_sold, 2))

k7, k8, k9 = st.columns(3)
with k7: kpi_card("👥 Active Customers", millify(Active_Customers, 2))
with k8: kpi_card("💵 Avg Deal Value", "$" + millify(avg_deal_value, 2))
with k9: kpi_card("📅 Periods Shown", ", ".join(selected_months))


# ------------------------------------------
# VISUALS
# ------------------------------------------


# ------------------------------------------
# sector dominance by country
# ------------------------------------------


sector_dominance = (filtered.groupby(['office_location','sector'])['revenue_won']
                    .sum().reset_index())
fig = px.bar(sector_dominance,
             x = 'office_location',
             y = 'revenue_won',
            color = 'sector',
            title = 'Sector Dominance by Country',
            color_discrete_sequence=px.colors.qualitative.Set2)
fig.update_layout(barmode='relative', barnorm='percent')
st.subheader("🏬 Sector Dominance by Country")
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# revenue by account
# ------------------------------------------


rev_acc = (filtered.groupby('subsidiary_of')['revenue_won']
            .sum().reset_index().sort_values('revenue_won',ascending = False)
            .head(10).sort_values('revenue_won',ascending = True))
fig = px.bar(rev_acc,
             x = 'revenue_won',
             y = 'subsidiary_of',
            title = 'Revenue by Account',
            orientation = 'h',
            color_discrete_sequence=px.colors.qualitative.Set2)
st.subheader("💰 Revenue by Account")
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# no of opportunities per account
# ------------------------------------------


opp_acc= (filtered.groupby('account')[['won_opportunities','lost_opportunities','open_opportunities']]
          .sum().reset_index().sort_values('won_opportunities',ascending = False).head(10).sort_values('won_opportunities',ascending = True)
         )

opp_long = opp_acc.melt(
    id_vars='account',
    value_vars=['won_opportunities','lost_opportunities','open_opportunities'],
    var_name='Opportunity_Type',
    value_name='Total_Opportunities'
)

fig = px.bar(
    opp_long,
    x='Total_Opportunities',
    y='account',
    color='Opportunity_Type',
    title='Total Opportunities per Account (Grouped)',
    orientation='h',
    barmode='group',
    text_auto=True,
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.subheader("🎁 Total Opportunities per Account")
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# winrate per sector
# ------------------------------------------


win_rate_sector = (filtered.groupby('sector')
                   .agg(
                       total = ('total_opportunities',sum),
                       won = ('won_opportunities','sum')
                        ).reset_index()
                    )
win_rate_sector['win_rate'] = (win_rate_sector['won']/win_rate_sector['total'] * 100).round(2)
fig = px.bar(win_rate_sector,
             x = 'sector',
             y = 'win_rate',
             title= 'Win Rate by Sector %',
             text= 'win_rate',
             color = 'win_rate',
             color_continuous_scale=[
        "#C8EAE2",   
        "#66C2A5",   
        "#2F8F83"    
    ]
)

fig.update_layout(
    xaxis_title = "Sector",
    yaxis_title = "Win Rate %",
    template = "plotly_white"
)
st.subheader("📈 Win Rate by Sector")
st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------
# AVG SALES CYCLE BY SECTOR
# ------------------------------------------

avg_sales_cycle = (
    filtered.groupby('sector')['avg_sales_cycle_days']
    .mean()
    .reset_index()
    .sort_values('avg_sales_cycle_days',ascending= False)   # optional sort
)


fig = px.line(
    avg_sales_cycle,
    x='sector',
    y='avg_sales_cycle_days',
    title='Avg Sales Cycle (Days) by Sector',
    markers=True,   # adds points to the line
)

fig.update_traces(
    line=dict(color="#66C2A5", width=3),      # green line
    marker=dict(size=8, color="#2F8F83")      # darker green markers
)

fig.update_layout(
    xaxis_title="Sector",
    yaxis_title="Avg Sales Cycle (Days)",
    template="simple_white",
)
st.subheader("🕛 Average Sales Cycle by Sector")
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# Avg deal value by sector 
# ------------------------------------------
sec_deal = (filtered.groupby('sector')['avg_win_deal_value'].mean().reset_index())

fig = px.line(
    sec_deal,
    x='sector',
    y = 'avg_win_deal_value',
    title= 'Avg Deal Value by Sector',
    markers= True,
            )

fig.update_traces(
    line=dict(color="#66C2A5", width=3),      # green line
    marker=dict(size=8, color="#2F8F83")      # darker green markers
)

fig.update_layout(
    xaxis_title = "Sector",
    yaxis_title = "Avg Deal Value",
    template = "simple_white",
)
st.subheader("💼 Average Deal Value by Sector")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# raw table
# ------------------------------------------

st.subheader("📄 Raw Data")
st.dataframe(account360)