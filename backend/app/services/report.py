from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

def _money(v): return f"INR {float(v or 0):,.0f}"

def build_pdf(path,client_name,request,analysis,content=None):
    content=content or {}
    doc=SimpleDocTemplate(path,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=15*mm,bottomMargin=15*mm,title=f"FinSight Financial Analysis - {request['business_name']}")
    base=getSampleStyleSheet(); teal=colors.HexColor('#0d8f92'); dark=colors.HexColor('#08212a'); muted=colors.HexColor('#58727c')
    styles={
      'title':ParagraphStyle('FS_Title',parent=base['Title'],fontSize=23,textColor=dark,spaceAfter=4),
      'sub':ParagraphStyle('FS_Sub',parent=base['Normal'],fontSize=9,textColor=muted,spaceAfter=9),
      'h':ParagraphStyle('FS_H',parent=base['Heading2'],fontSize=14,textColor=dark,spaceBefore=10,spaceAfter=7),
      'body':ParagraphStyle('FS_Body',parent=base['BodyText'],fontSize=9.2,leading=13,textColor=dark,spaceAfter=5),
      'small':ParagraphStyle('FS_Small',parent=base['BodyText'],fontSize=7.5,leading=10,textColor=muted),
      'finding':ParagraphStyle('FS_Find',parent=base['BodyText'],fontSize=8.5,leading=12,leftIndent=7,spaceAfter=5,textColor=dark),
    }
    story=[]
    story += [Paragraph('FINSIGHT ANALYTICS',styles['title']),Paragraph(f"Financial Performance & Cost Optimization Report — {request['business_name']}",styles['h']),Paragraph(f"Prepared for <b>{client_name}</b> · {request.get('business_type','Business')} · Request #{request['_id']}",styles['sub'])]
    meta=[[Paragraph('<b>Reporting period</b>',styles['small']),Paragraph(str(request.get('period_from','—'))+' to '+str(request.get('period_to','—')),styles['small']),Paragraph('<b>Status</b>',styles['small']),Paragraph('Analyst Review',styles['small'])]]
    mt=Table(meta,colWidths=[35*mm,55*mm,25*mm,55*mm]); mt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eef7f7')),('BOX',(0,0),(-1,-1),.5,teal),('INNERGRID',(0,0),(-1,-1),.25,colors.HexColor('#c7dddd')),('PADDING',(0,0),(-1,-1),6)])); story += [mt,Spacer(1,8)]
    story.append(Paragraph('Executive financial snapshot',styles['h']))
    metrics=[['Revenue','Expenses','Net Profit','Net Margin'],[_money(analysis.get('revenue')), _money(analysis.get('expenses')), _money(analysis.get('profit')), f"{float(analysis.get('margin',0)):.2f}%"]]
    t=Table(metrics,colWidths=[43*mm]*4); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),dark),('TEXTCOLOR',(0,0),(-1,0),colors.white),('BACKGROUND',(0,1),(-1,1),colors.HexColor('#f4f9f9')),('TEXTCOLOR',(0,1),(-1,1),dark),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,1),'Helvetica-Bold'),('ALIGN',(0,0),(-1,-1),'CENTER'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b8cdd1')),('PADDING',(0,0),(-1,-1),8)])); story += [t,Spacer(1,8)]
    rev=float(analysis.get('revenue') or 0); exp=float(analysis.get('expenses') or 0); ratio=(exp/rev*100) if rev else 0
    story.append(Paragraph(f"<b>Interpretation:</b> The detected expense-to-revenue ratio is {ratio:.1f}%. The analysis focuses on profitability, the largest cost drivers and practical opportunities for tighter financial control.",styles['body']))
    story.append(Paragraph('Analysis methodology',styles['h']))
    for n,txt in enumerate(['Validate the client request and reporting period.','Review available CSV/XLSX financial fields and aggregate numeric revenue, expense and cost values.','Calculate profit and net margin and rank detected cost/expense categories.','Summarize material observations as findings and management actions.','Review the result internally before client delivery.'],1): story.append(Paragraph(f'<b>{n}.</b> {txt}',styles['body']))
    cats=analysis.get('expense_categories') or {}
    if cats:
      story.append(Paragraph('Cost structure',styles['h']))
      rows=[['Cost / expense category','Amount','Share of detected costs']]
      total=sum(float(v or 0) for v in cats.values()) or 1
      for k,v in sorted(cats.items(),key=lambda kv:float(kv[1] or 0),reverse=True): rows.append([str(k),_money(v),f"{float(v or 0)/total*100:.1f}%"])
      rows.append(['Total',_money(total),'100.0%'])
      ct=Table(rows,colWidths=[92*mm,42*mm,36*mm],repeatRows=1); ct.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),teal),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c1d0d4')),('ALIGN',(1,1),(-1,-1),'RIGHT'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#eef7f7')),('PADDING',(0,0),(-1,-1),6)])); story += [ct]
    story.append(Paragraph('Executive summary',styles['h']))
    story.append(Paragraph(content.get('executive_summary') or 'This report summarizes the financial information reviewed by FinSight Analytics.',styles['body']))
    story.append(Paragraph('Key findings',styles['h']))
    findings=content.get('findings') or analysis.get('findings') or ['No material findings were generated from the available dataset.']
    for i,f in enumerate(findings,1): story.append(Paragraph(f'<b>{i}.</b> {f}',styles['finding']))
    story.append(Paragraph('Recommended management actions',styles['h']))
    actions=content.get('recommendations') or ['Review the largest cost category monthly and compare supplier or operating rates.','Track budget versus actual performance and investigate material variances.','Review pricing and contribution margins before accepting low-margin work.','Monitor receivables, inventory and operating cash requirements alongside profit.','Re-run the analysis after the next reporting period to measure improvement.']
    for i,x in enumerate(actions,1): story.append(Paragraph(f'<b>{i}.</b> {x}',styles['finding']))
    cs=content.get('case_study') or {}
    if cs:
        story.append(Paragraph('Case Study Decision',styles['h']))
        oa=cs.get('option_a') or {}; ob=cs.get('option_b') or {}
        a_adv=oa.get('advantages') or []; b_adv=ob.get('advantages') or []
        rows=[[oa.get('name','Option A'),'Advantages',ob.get('name','Option B')]]
        for i in range(max(len(a_adv),len(b_adv))): rows.append([a_adv[i] if i<len(a_adv) else '', '', b_adv[i] if i<len(b_adv) else ''])
        t=Table(rows,colWidths=[58*mm,45*mm,67*mm],repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),dark),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c1d0d4')),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),6)]))
        story += [t,Spacer(1,7)]
        da=oa.get('disadvantages') or []; db=ob.get('disadvantages') or []
        rows=[[oa.get('name','Option A'),'Disadvantages',ob.get('name','Option B')]]
        for i in range(max(len(da),len(db))): rows.append([da[i] if i<len(da) else '', '', db[i] if i<len(db) else ''])
        t=Table(rows,colWidths=[58*mm,45*mm,67*mm],repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),dark),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c1d0d4')),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),6)]))
        story += [t,Spacer(1,7)]
        story.append(Paragraph(f"<b>Final Decision:</b> {cs.get('final_decision','')}",styles['body']))
        story.append(Paragraph(f"<b>Considering:</b> {cs.get('considering','')}",styles['body']))
    if content.get('analyst_notes'):
        story.append(Paragraph('Analyst notes',styles['h']))
        story.append(Paragraph(content['analyst_notes'],styles['body']))
    story += [Spacer(1,8),Paragraph('FinSight delivery note',styles['h']),Paragraph('This report is based on the financial data provided for review. It is not an audited financial statement. Management should validate source records and assumptions before making financial decisions.',styles['small']),Spacer(1,12),Paragraph('Prepared by FinSight Analytics · Understand. Analyze. Improve.',styles['small'])]
    doc.build(story)
