import pandas as pd


# ---- IMPORT ALL 8 TABLES ----
products        = pd.read_csv("Resources/products.csv")
sales_teams     = pd.read_csv("Resources/sales_agent.csv")
accounts        = pd.read_csv("Resources/accounts.csv")
sales_pipeline  = pd.read_csv("Resources/sales_pipeline.csv")
product_360     = pd.read_csv("Resources/product_360.csv")
sales_agent_360 = pd.read_csv("Resources/sales_agent_360.csv")
cohort_raw      = pd.read_csv("CResources/cohort_raw.csv")
account_360     = pd.read_csv("Resources/account_360.csv")



