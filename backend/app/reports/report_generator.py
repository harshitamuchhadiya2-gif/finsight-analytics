from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def _money(x): return f"₹{float(x):,.2f} Cr"
def _pct(x): return f"{float(x)*100:.2f}%"
def _x(x): return f"{float(x):.2f}x"
def _num(x): return f"{float(x):,.2f}"

def _table(rows, widths=None):
    t=Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102A43")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F5F8FA")]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    return t

def generate_report(payload: dict, output_path: str) -> str:
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    result=payload["analysis"]; ratios=result["ratios"]
    client=payload.get("client",{})
    project=payload.get("project",{})
    rec=payload.get("recommendation","Management review recommended based on the financial evidence provided.")
    doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover",parent=styles["Title"],fontSize=26,leading=31,textColor=colors.HexColor("#102A43"),alignment=TA_CENTER,spaceAfter=12))
    styles.add(ParagraphStyle(name="Section",parent=styles["Heading1"],fontSize=16,leading=20,textColor=colors.HexColor("#0B7285"),spaceBefore=10,spaceAfter=8))
    styles.add(ParagraphStyle(name="Small",parent=styles["BodyText"],fontSize=8.5,leading=12,textColor=colors.HexColor("#475569")))
    story=[]
    story += [Spacer(1,35*mm),Paragraph("FinSight Analytics",styles["Cover"]),
              Paragraph("Financial Health & Business Performance Report",styles["Heading2"]),
              Spacer(1,8*mm),
              Paragraph(f"<b>Client:</b> {client.get('name','Client')}<br/><b>Industry:</b> {client.get('industry','—')}<br/><b>Analysis period:</b> {client.get('period','—')}<br/><b>Generated:</b> {datetime.now(timezone.utc).strftime('%d %b %Y')}",styles["BodyText"]),
              Spacer(1,25*mm),Paragraph("Confidential • Prepared for management decision-making",styles["Small"]),PageBreak()]

    story += [Paragraph("1. Executive Summary",styles["Section"]),
              Paragraph(f"<b>Overall financial health:</b> {result['health']}",styles["BodyText"]),Spacer(1,4*mm),
              Paragraph(rec,styles["BodyText"]),Spacer(1,5*mm)]
    story += [_table([["KPI","Value"],
                      ["Gross margin",_pct(ratios["gross_margin"])],
                      ["EBITDA margin",_pct(ratios["ebitda_margin"])],
                      ["Net profit margin",_pct(ratios["net_margin"])],
                      ["ROA",_pct(ratios["roa"])],["ROE",_pct(ratios["roe"])],
                      ["Current ratio",_x(ratios["current_ratio"])],
                      ["Quick ratio",_x(ratios["quick_ratio"])],
                      ["Debt / Equity",_x(ratios["debt_equity"])],
                      ["Interest coverage",_x(ratios["interest_coverage"])]]),
              Spacer(1,6*mm)]

    story += [Paragraph("2. Profit & Loss Analysis",styles["Section"])]
    pnl=payload.get("pnl",{})
    for key,title in [("revenue","Revenue"),("cogs","Cost of goods sold"),("gross_profit","Gross profit"),("opex","Operating expenses"),
                      ("ebitda","EBITDA"),("depreciation","Depreciation"),("ebit","EBIT"),("interest","Interest"),("pbt","PBT"),("tax","Tax"),("pat","PAT")]:
        if key in pnl:
            story.append(_table([["Particulars","Value"],[title,_money(pnl[key].get(result["base_year"],0))]])); story.append(Spacer(1,2*mm))

    story += [Paragraph("3. Balance Sheet Analysis",styles["Section"])]
    bs=payload.get("bs",{})
    rows=[["Particulars","Value"]]
    labels={"fixed_assets":"Fixed assets (net)","inventory":"Inventory","receivables":"Trade receivables","cash":"Cash & equivalents",
            "total_assets":"Total assets","equity":"Equity","long_term_debt":"Long-term debt","short_term_borrowings":"Short-term borrowings",
            "payables":"Trade payables","other_current_liabilities":"Other current liabilities"}
    for k,l in labels.items():
        if k in bs: rows.append([l,_money(bs[k].get(result["base_year"],0))])
    story += [_table(rows),Spacer(1,6*mm)]

    story += [Paragraph("4. Cash Flow Analysis",styles["Section"])]
    cfs=result.get("cash_flow",{})
    rows=[["Particulars","Value"]]+[[k.replace("_"," ").title(),_money(v)] for k,v in cfs.items() if isinstance(v,(int,float))]
    story += [_table(rows or [["Particulars","Value"],["No cash-flow data supplied","—"]]),PageBreak()]

    story += [Paragraph("5. Ratio Analysis",styles["Section"])]
    rows=[["Ratio","Result"],
          ["Gross profit margin",_pct(ratios["gross_margin"])],["EBITDA margin",_pct(ratios["ebitda_margin"])],
          ["Net profit margin",_pct(ratios["net_margin"])],["ROA",_pct(ratios["roa"])],["ROE",_pct(ratios["roe"])],
          ["Current ratio",_x(ratios["current_ratio"])],["Quick ratio",_x(ratios["quick_ratio"])],
          ["Debt / Equity",_x(ratios["debt_equity"])],["Interest coverage",_x(ratios["interest_coverage"])],
          ["Inventory days",_num(ratios["inventory_days"])],["Receivable days",_num(ratios["receivable_days"])],
          ["Payable days",_num(ratios["payable_days"])],["Cash conversion cycle",_num(ratios["cash_conversion_cycle"])]]
    story += [_table(rows),Spacer(1,6*mm)]

    story += [Paragraph("6. Incremental Free Cash Flow & Capital Budgeting",styles["Section"])]
    pr=result["project"]
    story += [_table([["Metric","Result"],["Initial outlay",_money(project.get("initial_outlay",0))],
                      ["NPV",_money(pr["npv"])],["IRR",_pct(pr["irr"]) if pr["irr"] is not None else "N/A"],
                      ["Payback period",f"{pr['payback_years']:.2f} years" if pr["payback_years"] is not None else "N/A"]]),Spacer(1,6*mm)]

    story += [Paragraph("7. Valuation",styles["Section"])]
    rv=result["relative_valuation"]
    story += [_table([["Metric","Value"],["Current EBITDA",_money(rv["current_ebitda"])],
                      ["EV / EBITDA multiple",_x(rv["multiple"])],["Relative enterprise value",_money(rv["enterprise_value"])]])]

    story += [Paragraph("8. Sensitivity Analysis",styles["Section"]),
              Paragraph("The case-study instructions require sales 10% below forecast and EBITDA margin 3 percentage points below the base case. Supply scenario outputs in payload['sensitivity'] when client data supports them.",styles["BodyText"])]
    sens=payload.get("sensitivity",[])
    if sens:
        story.append(Spacer(1,4*mm)); story.append(_table([["Scenario","NPV","IRR","Payback"]]+[[s["name"],_money(s.get("npv",0)),_pct(s["irr"]) if s.get("irr") is not None else "N/A",str(s.get("payback","N/A"))] for s in sens]))

    story += [Paragraph("9. Financing Options & Final Decision",styles["Section"])]
    financing=payload.get("financing",[])
    if financing:
        story.append(_table([["Option","Advantages","Disadvantages"]]+[[x["option"],x.get("advantages",""),x.get("disadvantages","")] for x in financing]))
    story += [Spacer(1,5*mm),Paragraph(f"<b>Final decision:</b> {payload.get('decision','Pending management approval.')}",styles["BodyText"]),
              Spacer(1,5*mm),Paragraph("Important: This report is an analytical aid and should be reviewed by qualified finance/accounting professionals before investment, lending, tax, or other material decisions.",styles["Small"])]
    doc.build(story)
    return str(out)
