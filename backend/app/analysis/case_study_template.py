# FinSight input contract modeled on the supplied Case Study.xlsx.
# Values are in ₹ crore unless a ratio/rate is explicitly used.

CASE_STUDY_INPUT_TEMPLATE = {
    "client": {"name":"", "industry":"", "period":"Y1-Y8"},
    "years":["Y1","Y2","Y3","Y4","Y5","Y6","Y7","Y8"],
    "pnl": {
        "revenue":{}, "cogs":{}, "gross_profit":{}, "opex":{}, "ebitda":{},
        "depreciation":{}, "ebit":{}, "interest":{}, "pbt":{}, "tax":{}, "pat":{}
    },
    "bs": {
        "fixed_assets":{}, "inventory":{}, "receivables":{}, "cash":{},
        "other_current_assets":{}, "total_assets":{}, "equity":{},
        "long_term_debt":{}, "short_term_borrowings":{}, "payables":{},
        "other_current_liabilities":{}
    },
    "cfs": {"cfo":0,"cfi":0,"cff":0,"loan_repayment":0,"interest":0,"dividend":0,"net_change_in_cash":0},
    "project": {
        "initial_outlay":120,
        "plant_machinery":90,
        "working_capital":20,
        "brand_launch":10,
        "discount_rate":0.12,
        "cash_flows":[]
    },
    "valuation": {"current_ebitda":0, "ev_ebitda_multiple":12},
    "sensitivity": [],
    "financing": [],
    "decision": ""
}
