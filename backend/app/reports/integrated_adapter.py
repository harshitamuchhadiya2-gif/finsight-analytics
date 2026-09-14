from pathlib import Path
from app.reports.report_generator import generate_report

def generate_integrated_report(*, client, request, analysis, output_path):
    payload={"client":{"name":client.get("full_name","Client"),"industry":client.get("business_type","—"),"period":f"{request.get('period_from','—')} – {request.get('period_to','—')}"},"project":{},"recommendation":"Management review recommended based on the financial evidence provided.","analysis":{"base_year":"Y3","health":"Needs attention","ratios":{"gross_margin":float(analysis.get("margin",0))/100,"ebitda_margin":0,"net_margin":float(analysis.get("margin",0))/100,"roa":0,"roe":0,"current_ratio":0,"quick_ratio":0,"debt_equity":0,"interest_coverage":0,"inventory_days":0,"receivable_days":0,"payable_days":0,"cash_conversion_cycle":0},"project":{"npv":0,"irr":None,"payback_years":None},"relative_valuation":{"current_ebitda":0,"multiple":12,"enterprise_value":0},"cash_flow":{}},"pnl":{},"bs":{},"sensitivity":[],"financing":[],"decision":"Pending management approval."}
    generate_report(payload,str(Path(output_path)))
    return str(output_path)
