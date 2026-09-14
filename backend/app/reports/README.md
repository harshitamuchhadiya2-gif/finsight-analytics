# FinSight Report Module

Install:
`pip install reportlab`

Use:
```python
from app.analysis.financial_analysis import analyze
from app.reports.report_generator import generate_report

result = analyze(payload)
payload["analysis"] = result
generate_report(payload, "generated/report.pdf")
```

The supplied Case Study.xlsx is used as the structural reference:
Tasks, P&L, BS, CFS, Ratio Analysis, DCF (legacy/new business),
Enterprise Value, Capital Budgeting, Financing, Option A, Option B, Decision.

Do not hard-code client results. Import/validate each client's supplied data,
calculate from that data, store the analysis/report metadata in MongoDB,
then generate the PDF.
