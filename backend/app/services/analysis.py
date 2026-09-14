from pathlib import Path
import pandas as pd

def _read_tables(path):
    ext=Path(path).suffix.lower()
    if ext=='.csv': return [('CSV', pd.read_csv(path))]
    if ext in {'.xlsx','.xlsm','.xls'}:
        return [(str(name), df) for name, df in pd.read_excel(path, sheet_name=None).items()]
    raise ValueError('Analysis supports CSV/XLSX files. PDF files can be stored for analyst review.')

def _numeric(series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce').fillna(0)
    cleaned=(series.astype(str).str.replace(r'[₹$€£,]', '', regex=True).str.replace(r'\s+', '', regex=True))
    return pd.to_numeric(cleaned, errors='coerce').fillna(0)

def _financial_score(df):
    names=[str(c).strip().lower() for c in df.columns]
    score=0
    for n in names:
        if any(k in n for k in ['revenue','sales','income']): score+=5
        if any(k in n for k in ['expense','expenses','cost','amount']): score+=3
        if any(k in n for k in ['profit','margin']): score+=2
    return score + min(len(df.columns),10)*0.1

def analyze_files(files):
    candidates=[]
    for f in files:
        try:
            candidates.extend([(f.get('original_name','File'), df) for _,df in _read_tables(f['stored_name']) if not df.empty])
        except Exception:
            continue
    if not candidates: raise ValueError('No analyzable CSV/XLSX file was found.')
    # Prefer the most financial-looking sheet instead of blindly reading the first Excel tab.
    source_name, df=max(candidates, key=lambda x:_financial_score(x[1]))
    lower={str(c).strip().lower():c for c in df.columns}
    def matching_cols(kind):
        exact={
          'revenue':['revenue','total revenue','sales','total sales','sales amount','revenue (₹)','revenue (rs)'],
          'expenses':['expenses','expense','total expenses','cost','total cost','total_cost','total cost (₹)','expense amount','amount (₹)'],
          'profit':['profit','net profit','gross profit','net_profit'],
        }
        keys=exact[kind]
        cols=[]
        for n,c in lower.items():
            if n in keys or any(k in n for k in keys if len(k)>4): cols.append(c)
        return cols
    def sum_cols(cols):
        return sum(float(_numeric(df[c]).sum()) for c in cols) if cols else 0.0

    revenue=sum_cols(matching_cols('revenue'))
    profit=sum_cols(matching_cols('profit'))
    expense_cols=matching_cols('expenses')
    # If a total-cost field exists, use it. Otherwise sum separate cost/expense fields.
    total_cost=[c for c in expense_cols if 'total' in str(c).lower() or 'expense' in str(c).lower() and 'category' not in str(c).lower()]
    expenses=sum_cols(total_cost[:1] if total_cost else expense_cols)

    # Support simple two-column sheets such as Category/Amount where labels identify revenue/cost/profit.
    if revenue==0 and len(df.columns)>=2:
        label_col=df.columns[0]; value_col=df.columns[1]
        vals=_numeric(df[value_col])
        labels=df[label_col].astype(str).str.lower()
        rev_mask=labels.str.contains('revenue|sales|income',regex=True,na=False)
        exp_mask=labels.str.contains('expense|cost|purchase',regex=True,na=False)
        prof_mask=labels.str.contains('profit',regex=True,na=False)
        if rev_mask.any(): revenue=float(vals[rev_mask].sum())
        if expenses==0 and exp_mask.any(): expenses=float(vals[exp_mask].sum())
        if profit==0 and prof_mask.any(): profit=float(vals[prof_mask].sum())

    if profit==0 and revenue: profit=revenue-expenses
    if expenses==0 and revenue and profit: expenses=revenue-profit
    margin=(profit/revenue*100) if revenue else 0

    category_data={}
    for c in df.columns:
        name=str(c).strip().lower()
        if any(k in name for k in ['expense','cost']) and 'total' not in name and 'category' not in name and pd.api.types.is_numeric_dtype(df[c]) or (any(k in name for k in ['expense','cost']) and 'total' not in name and 'category' not in name):
            v=float(_numeric(df[c]).sum())
            if v: category_data[str(c)]=round(v,2)
    if not category_data:
        # Common transaction structure: individual cost columns.
        for c in df.columns:
            name=str(c).lower()
            if any(k in name for k in ['raw material','labour','transport','maintenance','power','utilities','other cost']):
                v=float(_numeric(df[c]).sum())
                if v: category_data[str(c)]=round(v,2)
    if not category_data and expenses and len(df.columns)>=2:
        label_col=df.columns[0]; value_col=df.columns[1]; vals=_numeric(df[value_col]); labels=df[label_col].astype(str)
        for label,v in zip(labels,vals):
            if float(v)>0 and any(k in str(label).lower() for k in ['expense','cost','purchase']): category_data[str(label)]=category_data.get(str(label),0)+float(v)
    findings=[]
    if revenue and margin<10: findings.append('Profit margin is below 10%; review major cost drivers.')
    if expenses and revenue and expenses/revenue>0.7: findings.append('Expenses exceed 70% of revenue; identify high-cost categories.')
    if category_data: findings.append(f"Largest detected cost/expense field: {max(category_data,key=category_data.get)}.")
    findings.append(f'Dataset contains {len(df):,} rows across {len(df.columns)} columns.')
    return {'revenue':round(revenue,2),'expenses':round(expenses,2),'profit':round(profit,2),'margin':round(margin,2),'expense_categories':category_data,'findings':findings,'source_sheet':source_name}
