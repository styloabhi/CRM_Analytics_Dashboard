import streamlit as st
# 🔐 Page security check
if st.session_state["authentication_status"] != True:
    st.error("Please login first.")
    st.stop()


# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from millify import millify


# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(
    page_title="Sales Agent 360 Dashboard",
    page_icon="👨‍💼",
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
            👨‍💼 Sales Agent 360 Dashboard
        </h1>
        <p style='font-size:20px; color:#5a6a81; font-weight:500;'>
            Comprehensive Performance View Across All Sales Agents
        </p>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# LOAD DATA
# ----------------------------
sa360 = pd.read_csv("Resources/sales_agent_360.csv")
sa360['first_engage_date'] = pd.to_datetime(sa360['first_engage_date'],format = '%d-%m-%Y')
sa360['last_close_date']= pd.to_datetime(sa360['last_close_date'],format = '%d-%m-%Y')

sa360['month_num'] = sa360['first_engage_date'].dt.month
sa360['month_name'] = sa360['first_engage_date'].dt.month_name()


# ----------------------------
# CREATE SLICER LISTS
# ----------------------------
month_list = (
    sa360[['month_num','month_name']]
    .dropna()
    .drop_duplicates()
    .sort_values("month_num")["month_name"]
    .tolist()
)

agent_list = sorted(sa360['sales_agent'].dropna().unique())
region_list = sorted(sa360['regional_office'].dropna().unique())


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

    # ------------------ Agent SLICER ------------------
    st.markdown("<div class='sidebar-label'>👨‍💼 Select Agent</div>", unsafe_allow_html=True)
    selected_agent = st.multiselect("Select Agent", agent_list)
    if not selected_agent:
        selected_agent = agent_list

    # ------------------ Region SLICER ------------------
    st.markdown("<div class='sidebar-label'>🧩 Select Sector</div>", unsafe_allow_html=True)
    selected_region = st.multiselect("Select Sector", region_list)
    if not selected_region:
        selected_region =  region_list 


# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered = sa360[
    sa360["month_name"].isin(selected_months) &
    sa360["regional_office"].isin(selected_region) &
    sa360["sales_agent"].isin(selected_agent)
]


# ----------------------------
# KPI VALUES
# ----------------------------
Total_Revenue = sa360['revenue_won'].sum()
Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)

Total_Opportunities = filtered['total_opportunities'].sum()
Open_Opportunities = filtered['open_opportunities'].sum()
Won_Opportunities = filtered['won_opportunities'].sum()
Lost_Opportunities = filtered['lost_opportunities'].sum()

Win_Rate = (Won_Opportunities / Total_Opportunities * 100) if Total_Opportunities > 0 else 0
Active_Customers = len(filtered)
avg_deal_value = filtered['avg_win_deal_value'].mean()
Customer_per_agent = filtered['distinct_accounts'].mean()
Avg_Sales_Cycle = filtered['avg_sales_cycle_days'].mean()
agent_Count = filtered['sales_agent'].nunique()

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
with k6: kpi_card("📦 Average Sales Cycle", millify(Avg_Sales_Cycle, 2))

k7, k8, k9 = st.columns(3)
with k7: kpi_card("👥 Customer Per Sales Agent", millify(Customer_per_agent, 2))
with k8: kpi_card("💵 Avg Deal Value", "$" + millify(avg_deal_value, 2))
with k9: kpi_card("📅 Total Sales Agent", (agent_Count))



# ------------------------------------------
# VISUALS
# ------------------------------------------

# ------------------------------------------
# Agent Revenue
# ------------------------------------------

agent_revenue = (filtered.groupby(['sales_agent'])['revenue_won'].sum().reset_index())
agent_revenue ['rev_fmt'] = agent_revenue['revenue_won'].apply(lambda x: millify(x,precision = 1))

fig = px.bar(agent_revenue,
             x = 'sales_agent',
             y = 'revenue_won',
             title = 'Revenue by Sales Agent',
             text= 'rev_fmt',
             color_discrete_sequence=px.colors.qualitative.Set2)
st.header("💰 Revenue by Sales Agent")
st.plotly_chart(fig,use_container_width= True)


# ------------------------------------------
# no of opportunities per agent
# ------------------------------------------
 
opp_sa = (filtered.groupby('sales_agent')[['won_opportunities','lost_opportunities','open_opportunities']]
          .sum().reset_index().sort_values('won_opportunities',ascending = False).head(10).sort_values('won_opportunities',ascending = True)
         )

opp_long = opp_sa.melt(
        id_vars= 'sales_agent',
        value_vars= ['won_opportunities','lost_opportunities','open_opportunities'],
        var_name= 'opportunity_type',
        value_name= 'total_opportunities'
)

fig = px.bar(
    opp_long,
    x = 'total_opportunities',
    y = 'sales_agent',
    color = 'opportunity_type',
    title= 'No of Opportunities Per Sales Agent',
    barmode= 'group',
    text_auto= True,
    color_discrete_sequence= px.colors.qualitative.Set2
)
st.header("🕛 Number of Opportunities Per Sales Agent")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# Avg deal value per agent
# ------------------------------------------

avg_del = (filtered.groupby('sales_agent')['avg_win_deal_value'].mean().reset_index().sort_values('avg_win_deal_value',ascending= False))
fig = px.line(avg_del,
              x = 'sales_agent',
              y = 'avg_win_deal_value',
              markers = True,
              color_discrete_sequence=px.colors.qualitative.Set2)
st.subheader("🕛 Average Deal Value by Sales_Agent")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# Win Rate % by Sales Agent
# ------------------------------------------

win_rate_agent = (filtered.groupby('sales_agent')
                    .agg(
                        total = ('total_opportunities','sum'),
                        won = ('won_opportunities','sum')
                    ).reset_index()
                    )
win_rate_agent['win_rate'] = (win_rate_agent['won']/win_rate_agent['total']* 100).round(2)
win_rate_agent = win_rate_agent.sort_values('win_rate', ascending=False)


fig = px.line(win_rate_agent,
             x = 'sales_agent',
             y = 'win_rate',
             markers = True,
              color_discrete_sequence=px.colors.qualitative.Set2) 

st.subheader("📈 Win Rate by Agent")
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# Account Coverage by Sales Agent
# ------------------------------------------

agco = (filtered.groupby('sales_agent')['distinct_accounts'].sum().reset_index().sort_values('distinct_accounts',ascending= False))

fig = px.bar(agco,
             x = 'sales_agent',
             y = 'distinct_accounts',
             title = 'Account Coverage by Sales agent',
             color_discrete_sequence=px.colors.qualitative.Set2,
             text_auto= True)
st.subheader("👨‍💼 Account Coverage by Sales agent")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# avg sales cycle
# ------------------------------------------

avg_sal = (filtered.groupby('sales_agent')['avg_sales_cycle_days'].mean()
           .reset_index().sort_values('avg_sales_cycle_days',ascending= False))

fig = px.line(
    avg_sal,
    x = 'sales_agent',
    y = 'avg_sales_cycle_days',
    title = 'Avg Sales Cycle (Days) by Sector',
     markers=True,
    color_discrete_sequence=px.colors.qualitative.Set2,
    text='avg_sales_cycle_days')

st.subheader(' 🏆 Average Sales Cycle (Days)')
st.plotly_chart(fig,use_container_width= True)


# ------------------------------------------
# regional sales
# ------------------------------------------

regs = filtered.groupby('regional_office')['revenue_won'].sum().reset_index()
fig = px.pie(
    regs,
    names='regional_office',
    values='revenue_won',
    title='Revenue Share by Regional Office',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(
    textinfo='percent+label',
    pull=[0.05]*len(regs)  
)

st.subheader("🌍 Revenue by Regional Office")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📄 Raw Data")
st.dataframe(filtered)



