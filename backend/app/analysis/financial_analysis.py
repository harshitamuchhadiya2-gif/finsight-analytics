from __future__ import annotations
from typing import Any
import math

def _n(v, default=0.0):
    try:
        if v is None or v == "": return default
        return float(v)
    except (TypeError, ValueError):
        return default

def pct(v): return round(_n(v) * 100, 2)
def safe_div(a,b): return _n(a)/_n(b) if _n(b) else 0.0

def analyze(data: dict[str, Any]) -> dict[str, Any]:
    pnl = data.get("pnl", {})
    bs = data.get("bs", {})
    cfs = data.get("cfs", {})
    years = data.get("years") or ["Y1","Y2","Y3"]
    y3 = "Y3" if "Y3" in years else years[-1]

    revenue = _n(pnl.get("revenue", {}).get(y3))
    cogs = _n(pnl.get("cogs", {}).get(y3))
    gross = _n(pnl.get("gross_profit", {}).get(y3), revenue-cogs)
    ebitda = _n(pnl.get("ebitda", {}).get(y3))
    ebit = _n(pnl.get("ebit", {}).get(y3))
    pat = _n(pnl.get("pat", {}).get(y3))
    assets = _n(bs.get("total_assets", {}).get(y3))
    equity = _n(bs.get("equity", {}).get(y3))
    debt = _n(bs.get("borrowings", {}).get(y3))
    current_assets = sum(_n(bs.get(k, {}).get(y3)) for k in
                         ["inventory","receivables","cash","other_current_assets"])
    current_liabilities = sum(_n(bs.get(k, {}).get(y3)) for k in
                              ["short_term_borrowings","payables","other_current_liabilities"])
    quick_assets = current_assets - _n(bs.get("inventory", {}).get(y3))

    ratios = {
        "gross_margin": safe_div(gross,revenue),
        "ebitda_margin": safe_div(ebitda,revenue),
        "net_margin": safe_div(pat,revenue),
        "roa": safe_div(pat,assets),
        "roe": safe_div(pat,equity),
        "current_ratio": safe_div(current_assets,current_liabilities),
        "quick_ratio": safe_div(quick_assets,current_liabilities),
        "debt_equity": safe_div(debt,equity),
        "interest_coverage": safe_div(ebitda, _n(pnl.get("interest", {}).get(y3))),
    }

    inv = _n(bs.get("inventory", {}).get(y3))
    rec = _n(bs.get("receivables", {}).get(y3))
    pay = _n(bs.get("payables", {}).get(y3))
    ratios.update({
        "inventory_days": safe_div(inv,cogs)*365,
        "receivable_days": safe_div(rec,revenue)*365,
        "payable_days": safe_div(pay,cogs)*365,
        "cash_conversion_cycle": safe_div(inv,cogs)*365 + safe_div(rec,revenue)*365 - safe_div(pay,cogs)*365,
    })

    project = data.get("project", {})
    cf = project.get("cash_flows", [])
    discount = _n(project.get("discount_rate"), .12)
    npv = 0.0
    for i, x in enumerate(cf, start=1):
        npv += _n(x) / ((1+discount)**i)
    initial = abs(_n(project.get("initial_outlay")))
    npv -= initial

    # IRR by bisection; robust for normal project cash flows.
    irr = None
    flows = [-initial] + [_n(x) for x in cf]
    if any(x > 0 for x in flows) and any(x < 0 for x in flows):
        lo, hi = -0.9999, 10.0
        for _ in range(200):
            r=(lo+hi)/2
            val=sum(x/((1+r)**i) for i,x in enumerate(flows))
            if val > 0: lo=r
            else: hi=r
        irr=(lo+hi)/2

    payback = None
    cumulative = -initial
    for i,x in enumerate(cf, start=1):
        prev=cumulative
        cumulative += _n(x)
        if cumulative >= 0:
            payback=(i-1)+abs(prev)/_n(x) if _n(x) else i
            break

    valuation = data.get("valuation", {})
    legacy_ebitda = _n(valuation.get("current_ebitda"), ebitda)
    multiple = _n(valuation.get("ev_ebitda_multiple"), 12)
    relative_ev = legacy_ebitda * multiple

    return {
        "base_year": y3,
        "ratios": ratios,
        "project": {"npv": npv, "irr": irr, "payback_years": payback},
        "relative_valuation": {"current_ebitda": legacy_ebitda, "multiple": multiple, "enterprise_value": relative_ev},
        "cash_flow": cfs,
        "health": "Strong" if ratios["ebitda_margin"] >= .15 and ratios["current_ratio"] >= 1.5 else
                  "Moderate" if ratios["ebitda_margin"] >= .08 else "Needs attention",
    }
