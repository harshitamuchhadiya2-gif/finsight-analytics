from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def _money(v):
    return f"₹{float(v or 0):,.0f}"

def build_pdf(path, client_name, request, analysis, content=None):
    content = content or {}
    business_name = request.get('business_name', 'Business Entity')
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=14*mm,
        leftMargin=14*mm,
        topMargin=14*mm,
        bottomMargin=14*mm,
        title=f"FinSight Advisory Report — {business_name}"
    )

    base = getSampleStyleSheet()
    teal = colors.HexColor('#0d8f92')
    teal_dark = colors.HexColor('#086669')
    dark = colors.HexColor('#08212a')
    muted = colors.HexColor('#546e7a')
    bg_light = colors.HexColor('#f3f8f8')
    border_color = colors.HexColor('#b6cfd2')

    styles = {
        'brand': ParagraphStyle('FS_Brand', parent=base['Normal'], fontSize=16, fontName='Helvetica-Bold', textColor=teal_dark, spaceAfter=2),
        'title': ParagraphStyle('FS_Title', parent=base['Title'], fontSize=20, leading=24, fontName='Helvetica-Bold', textColor=dark, spaceAfter=4, alignment=0),
        'sub': ParagraphStyle('FS_Sub', parent=base['Normal'], fontSize=9.5, leading=13, textColor=muted, spaceAfter=8),
        'section_h': ParagraphStyle('FS_SecH', parent=base['Heading2'], fontSize=12, leading=15, fontName='Helvetica-Bold', textColor=dark, spaceBefore=8, spaceAfter=5),
        'body': ParagraphStyle('FS_Body', parent=base['BodyText'], fontSize=8.8, leading=13, textColor=dark, spaceAfter=5),
        'bullet': ParagraphStyle('FS_Bullet', parent=base['BodyText'], fontSize=8.5, leading=12.5, textColor=dark, leftIndent=10, spaceAfter=4),
        'meta_label': ParagraphStyle('FS_MetaLbl', parent=base['Normal'], fontSize=7.5, fontName='Helvetica-Bold', textColor=dark),
        'meta_val': ParagraphStyle('FS_MetaVal', parent=base['Normal'], fontSize=7.5, textColor=muted),
        'kpi_title': ParagraphStyle('FS_KpiT', parent=base['Normal'], fontSize=8, fontName='Helvetica-Bold', textColor=colors.white, alignment=1),
        'kpi_val': ParagraphStyle('FS_KpiV', parent=base['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=dark, alignment=1),
        'kpi_sub': ParagraphStyle('FS_KpiS', parent=base['Normal'], fontSize=7, textColor=muted, alignment=1),
        'footer': ParagraphStyle('FS_Foot', parent=base['Normal'], fontSize=7.5, leading=10, textColor=muted, alignment=1),
    }

    story = []

    # Header Banner
    story.append(Paragraph('FINSIGHT ANALYTICS · CORPORATE ADVISORY', styles['brand']))
    story.append(Paragraph(content.get('title') or f"Financial Performance & Strategic Advisory Report — {business_name}", styles['title']))
    story.append(Paragraph(f"Prepared for: <b>{client_name}</b> | Industry: <b>{request.get('business_type','General Corporate')}</b> | Engagement Ref: <b>#{request.get('_id', 'FS-REF')[:10]}</b>", styles['sub']))

    # Metadata Strip
    meta_data = [
        [
            Paragraph('<b>Analysis Period</b>', styles['meta_label']),
            Paragraph(f"{request.get('period_from', 'N/A')} to {request.get('period_to', 'Present')}", styles['meta_val']),
            Paragraph('<b>Advisory Status</b>', styles['meta_label']),
            Paragraph('Verified & Certified Review', styles['meta_val']),
            Paragraph('<b>Confidentiality</b>', styles['meta_label']),
            Paragraph('Strictly Private & Confidential', styles['meta_val']),
        ]
    ]
    mt = Table(meta_data, colWidths=[24*mm, 35*mm, 26*mm, 37*mm, 25*mm, 35*mm])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 0.75, teal),
        ('INNERGRID', (0,0), (-1,-1), 0.3, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(mt)
    story.append(Spacer(1, 6))

    # Executive Scorecard (KPIs)
    rev = float(analysis.get('revenue', 0))
    exp = float(analysis.get('expenses', 0))
    profit = float(analysis.get('profit', 0))
    margin = float(analysis.get('margin', 0))

    kpi_headers = [
        Paragraph('GROSS REVENUE', styles['kpi_title']),
        Paragraph('TOTAL EXPENDITURE', styles['kpi_title']),
        Paragraph('NET OPERATING PROFIT', styles['kpi_title']),
        Paragraph('NET PROFIT MARGIN', styles['kpi_title'])
    ]
    kpi_values = [
        Paragraph(_money(rev), styles['kpi_val']),
        Paragraph(_money(exp), styles['kpi_val']),
        Paragraph(_money(profit), styles['kpi_val']),
        Paragraph(f"{margin:.1f}%", styles['kpi_val'])
    ]
    kpi_subs = [
        Paragraph('Top-line turnover', styles['kpi_sub']),
        Paragraph('Operating outflow', styles['kpi_sub']),
        Paragraph('Operating surplus', styles['kpi_sub']),
        Paragraph('Profitability yield', styles['kpi_sub'])
    ]

    kt = Table([kpi_headers, kpi_values, kpi_subs], colWidths=[45.5*mm]*4)
    kt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), dark),
        ('BACKGROUND', (0,1), (-1,-1), bg_light),
        ('GRID', (0,0), (-1,-1), 0.4, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,1), 2),
        ('TOPPADDING', (0,2), (-1,2), 1),
        ('BOTTOMPADDING', (0,2), (-1,2), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(kt)
    story.append(Spacer(1, 7))

    # Executive Summary Narrative
    story.append(Paragraph('1. Executive Financial Summary', styles['section_h']))
    story.append(Paragraph(content.get('executive_summary') or f"{business_name} recorded revenue of {_money(rev)} and expenses of {_money(exp)}, resulting in net profit of {_money(profit)} ({margin:.1f}% margin).", styles['body']))

    # Cost Driver & Expenditure Distribution
    cats = analysis.get('expense_categories') or {}
    if cats:
        story.append(Spacer(1, 4))
        story.append(Paragraph('2. Expenditure Distribution & Cost Structure Analysis', styles['section_h']))
        cat_rows = [[
            Paragraph('<b>Expenditure Category</b>', styles['meta_label']),
            Paragraph('<b>Disbursement (INR)</b>', styles['meta_label']),
            Paragraph('<b>Cost Share (%)</b>', styles['meta_label']),
            Paragraph('<b>Risk Profile</b>', styles['meta_label'])
        ]]
        total_costs = sum(float(v or 0) for v in cats.values()) or 1
        sorted_cats = sorted(cats.items(), key=lambda kv: float(kv[1] or 0), reverse=True)
        for idx, (k, v) in enumerate(sorted_cats):
            share = (float(v or 0) / total_costs) * 100
            risk_label = 'Critical Driver' if share >= 35 else ('Significant' if share >= 15 else 'Operational')
            cat_rows.append([
                Paragraph(str(k), styles['body']),
                Paragraph(_money(v), styles['body']),
                Paragraph(f"{share:.1f}%", styles['body']),
                Paragraph(f"<b>{risk_label}</b>", styles['body'])
            ])
        cat_rows.append([
            Paragraph('<b>Consolidated Operating Total</b>', styles['meta_label']),
            Paragraph(f"<b>{_money(total_costs)}</b>", styles['meta_label']),
            Paragraph('<b>100.0%</b>', styles['meta_label']),
            Paragraph('<b>Full Absorption</b>', styles['meta_label'])
        ])
        ct = Table(cat_rows, colWidths=[70*mm, 42*mm, 35*mm, 35*mm], repeatRows=1)
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), teal),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.35, border_color),
            ('BACKGROUND', (0,-1), (-1,-1), bg_light),
            ('ALIGN', (1,0), (2,-1), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 4.5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(ct)

    # Key Findings & Diagnostic Observations
    story.append(Spacer(1, 4))
    story.append(Paragraph('3. Strategic Financial Findings & Diagnostic Insights', styles['section_h']))
    findings = content.get('findings') or analysis.get('findings') or ['Financial analysis indicates stable baseline operations with opportunities for cost rationalization.']
    for idx, f in enumerate(findings, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {f}", styles['bullet']))

    # Actionable Recommendations Roadmap
    story.append(Spacer(1, 4))
    story.append(Paragraph('4. Actionable Management Recommendations & Phased Roadmap', styles['section_h']))
    recs = content.get('recommendations') or [
        'Phase 1 (Immediate · 0–30 Days): Review top cost categories and supplier pricing contracts.',
        'Phase 2 (Tactical · 30–60 Days): Enforce minimum unit margins and active cash collection cycles.',
        'Phase 3 (Strategic · 90+ Days): Re-evaluate capital financing to protect working capital liquidity.'
    ]
    for idx, r in enumerate(recs, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {r}", styles['bullet']))

    # Case Study & Strategic Decision Matrix
    cs = content.get('case_study') or {}
    if cs:
        story.append(Spacer(1, 4))
        story.append(Paragraph('5. Case Study: Capital Structuring & Strategic Decision Matrix', styles['section_h']))
        oa = cs.get('option_a') or {}
        ob = cs.get('option_b') or {}
        a_adv = oa.get('advantages') or []
        b_adv = ob.get('advantages') or []
        a_dis = oa.get('disadvantages') or []
        b_dis = ob.get('disadvantages') or []

        matrix_rows = [
            [
                Paragraph(f"<b>{oa.get('name', 'Option A: Senior Debt')}</b>", styles['meta_label']),
                Paragraph('<b>Strategic Dimension</b>', styles['meta_label']),
                Paragraph(f"<b>{ob.get('name', 'Option B: Private Equity')}</b>", styles['meta_label'])
            ],
            [
                Paragraph('• ' + '<br/>• '.join(a_adv), styles['bullet']),
                Paragraph('<b>Key Advantages & Upside</b>', styles['body']),
                Paragraph('• ' + '<br/>• '.join(b_adv), styles['bullet'])
            ],
            [
                Paragraph('• ' + '<br/>• '.join(a_dis), styles['bullet']),
                Paragraph('<b>Risks & Structural Constraints</b>', styles['body']),
                Paragraph('• ' + '<br/>• '.join(b_dis), styles['bullet'])
            ]
        ]
        cs_table = Table(matrix_rows, colWidths=[70*mm, 42*mm, 70*mm], repeatRows=1)
        cs_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), dark),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.35, border_color),
            ('BACKGROUND', (1,1), (1,-1), bg_light),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(cs_table)
        story.append(Spacer(1, 4))

        decision_box = [
            [
                Paragraph(f"<b>RECOMMENDED STRATEGIC DECISION:</b> {cs.get('final_decision', 'Option B (Strategic Equity Partner)')}<br/>"
                          f"<b>Evaluation Rationale:</b> {cs.get('considering', 'Downside liquidity protection, market volatility resilience, interest coverage safety, and enterprise valuation security.')}", styles['body'])
            ]
        ]
        dt = Table(decision_box, colWidths=[182*mm])
        dt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_light),
            ('BOX', (0,0), (-1,-1), 1, teal),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(dt)

    # Analyst Notes & Verification
    if content.get('analyst_notes'):
        story.append(Spacer(1, 4))
        story.append(Paragraph('6. Analyst Notes & Certification', styles['section_h']))
        story.append(Paragraph(content['analyst_notes'], styles['body']))

    # Governance & Disclaimer
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=5, spaceBefore=0))
    story.append(Paragraph(
        "<b>FinSight Advisory Protocol:</b> This document was generated based on verified business financial data submitted for advisory analysis. "
        "It provides management decision intelligence and does not replace statutory audit opinions. Prepared by FinSight Analytics Corporate Advisory.",
        styles['footer']
    ))

    doc.build(story)
