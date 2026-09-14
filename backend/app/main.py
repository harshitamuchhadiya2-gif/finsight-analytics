import os, uuid, secrets, hashlib, smtplib, base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from urllib.request import Request as UrlRequest, urlopen
from urllib.parse import urlencode
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.core.security import hash_password, verify_password, create_token
from app.core.config import MAX_UPLOAD_MB
from app.services.analysis import analyze_files
from app.services.report import build_pdf

ROOT=Path(__file__).resolve().parents[2]; UPLOAD_DIR=ROOT/'storage'/'uploads'; REPORT_DIR=ROOT/'storage'/'reports'; UPLOAD_DIR.mkdir(parents=True,exist_ok=True); REPORT_DIR.mkdir(parents=True,exist_ok=True)
ALLOWED={'.csv','.xlsx','.xls','.xlsm','.pdf'}; app=FastAPI(title='FinSight Analytics API',version='2.0.0')
CORS_ORIGINS=[x.strip() for x in os.getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return uuid.uuid4().hex

def user_out(u): return {'id':u.get('_id') or u.get('id'),'full_name':u.get('full_name'),'username':u.get('username'),'business_name':u.get('business_name'),'email':u.get('email'),'phone':u.get('phone'),'business_type':u.get('business_type'),'role':u.get('role')}
def request_out(r,db):
    files=list(db.files.find({'request_id':r['_id']}).sort('created_at',1)); reports=list(db.reports.find({'request_id':r['_id']}).sort('created_at',1))
    client=db.users.find_one({'_id':r['client_id']}) or {}; return {'id':r['_id'],'client_id':r['client_id'],'client_name':client.get('full_name','Client'),'client_email':client.get('email',''),'business_name':r['business_name'],'business_type':r.get('business_type',''),'period_from':r.get('period_from',''),'period_to':r.get('period_to',''),'requested_areas':r.get('requested_areas',[]),'additional_info':r.get('additional_info',''),'status':r.get('status','New'),'created_at':r['created_at'],'files':[{'id':x['_id'],'original_name':x['original_name'],'size':x['size'],'created_at':x['created_at']} for x in files],'reports':[{'id':x['_id'],'title':x['title'],'created_at':x['created_at'],'sent_at':x.get('sent_at'),'status':x.get('status','Delivered' if x.get('sent_at') else 'Ready')} for x in reports], 'growth':r.get('growth',[]), 'summary':r.get('summary',{})}
class RegisterIn(BaseModel):
    full_name:str=Field(min_length=2,max_length=120); username:str=Field(min_length=3,max_length=80); business_name:str=Field(min_length=2,max_length=160); email:EmailStr; phone:str=Field(min_length=7,max_length=40); business_type:str=Field(min_length=2,max_length=100); password:str=Field(min_length=8,max_length=128)
class LoginIn(BaseModel): login:str; password:str

class ForgotPasswordSendOtpIn(BaseModel):
    method:str=Field(pattern='^(email|phone)$')
    identifier:str=Field(min_length=5,max_length=160)

class ForgotPasswordVerifyOtpIn(BaseModel):
    reset_id:str=Field(min_length=10,max_length=100)
    otp:str=Field(min_length=6,max_length=6)

class ForgotPasswordResetIn(BaseModel):
    reset_token:str=Field(min_length=20,max_length=300)
    new_password:str=Field(min_length=8,max_length=128)

def normalize_phone(value:str)->str:
    digits=''.join(ch for ch in value if ch.isdigit())
    if digits.startswith('91') and len(digits)==12: digits=digits[2:]
    return digits

def hash_otp(value:str)->str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def hash_reset_token(value:str)->str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def mask_email(email:str)->str:
    email=str(email)
    if '@' not in email: return email
    name,domain=email.split('@',1)
    masked=(name[:1]+'*') if len(name)<=2 else (name[:2]+'*'*max(2,len(name)-2))
    return masked+'@'+domain

def mask_phone(phone:str)->str:
    digits=normalize_phone(phone)
    return digits[:2]+'******'+digits[-2:] if len(digits)==10 else '******'

def find_recovery_user(method:str,identifier:str,db):
    if method=='email':
        return db.users.find_one({'email':identifier.lower().strip()})
    phone=normalize_phone(identifier)
    if len(phone)!=10 or phone[0] not in '6789':
        raise HTTPException(422,'Please enter a valid Indian phone number.')
    for u in db.users.find({'$or':[{'phone':phone},{'phone':'+91'+phone},{'phone':'91'+phone}]}):
        if normalize_phone(str(u.get('phone','')))==phone: return u
    return None

def send_email_otp(email:str,otp:str):
    host=os.getenv('SMTP_HOST','').strip(); user=os.getenv('SMTP_USER','').strip(); password=os.getenv('SMTP_PASSWORD','').strip()
    if not host or not user or not password: return False
    port=int(os.getenv('SMTP_PORT','587')); sender=os.getenv('SMTP_FROM',user).strip()
    message=EmailMessage(); message['Subject']='FinSight Analytics — Password Reset OTP'; message['From']=sender; message['To']=email
    message.set_content(f'Your FinSight Analytics password reset OTP is {otp}. It is valid for 10 minutes. If you did not request this, ignore this message.')
    with smtplib.SMTP(host,port,timeout=20) as server:
        server.starttls(); server.login(user,password); server.send_message(message)
    return True

def send_sms_otp(phone:str,otp:str):
    sid=os.getenv('TWILIO_ACCOUNT_SID','').strip(); auth=os.getenv('TWILIO_AUTH_TOKEN','').strip(); sender=os.getenv('TWILIO_FROM','').strip()
    if not sid or not auth or not sender: return False
    destination='+91'+normalize_phone(phone)
    url=f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json'
    payload=urlencode({'To':destination,'From':sender,'Body':f'FinSight Analytics password reset OTP: {otp}. Valid for 10 minutes.'}).encode()
    credentials=base64.b64encode(f'{sid}:{auth}'.encode()).decode()
    req=UrlRequest(url,data=payload,headers={'Authorization':f'Basic {credentials}','Content-Type':'application/x-www-form-urlencoded'},method='POST')
    with urlopen(req,timeout=20) as response: response.read()
    return True
class RequestIn(BaseModel): business_name:str; business_type:str; period_from:str=''; period_to:str=''; requested_areas:list[str]=[]; additional_info:str=''
class StatusIn(BaseModel): status:str
class FinancialsIn(BaseModel): revenue:float=0; expenses:float=0; profit:float=0; margin:float=0; expense_categories:dict[str,float]={}; findings:list[str]=[]
class ReportEditIn(BaseModel): title:str='Financial Analysis Report'; executive_summary:str=''; findings:list[str]=[]; recommendations:list[str]=[]; analyst_notes:str=''; case_study:dict={}
class MessageIn(BaseModel): body:str=Field(min_length=1,max_length=3000)
@app.get('/api/health')
def health(db=Depends(get_db)):
    try: db.command('ping'); return {'ok':True,'service':'FinSight Analytics','database':'MongoDB'}
    except Exception as e: raise HTTPException(503,f'MongoDB connection failed: {e}')
@app.post('/api/auth/register')
def register(p:RegisterIn,db=Depends(get_db)):
    email=p.email.lower(); username=p.username.lower()
    if db.users.find_one({'email':email}): raise HTTPException(400,'Email already registered')
    if db.users.find_one({'username':username}): raise HTTPException(400,'Username already registered')
    u={'_id':uid(),'full_name':p.full_name,'username':username,'business_name':p.business_name,'email':email,'phone':p.phone,'business_type':p.business_type,'password_hash':hash_password(p.password),'role':'client','created_at':now()}; db.users.insert_one(u)
    return {'token':create_token(u['_id'],u['role']),'user':user_out(u)}
@app.post('/api/auth/login')
def login(p:LoginIn,db=Depends(get_db)):
    v=p.login.strip().lower(); u=db.users.find_one({'$or':[{'email':v},{'username':v}]})
    if not u or not verify_password(p.password,u['password_hash']): raise HTTPException(401,'Invalid email/username or password')
    return {'token':create_token(u['_id'],u['role']),'user':user_out(u)}

@app.post('/api/auth/forgot-password/send-otp')
def forgot_password_send_otp(p:ForgotPasswordSendOtpIn,db=Depends(get_db)):
    method=p.method.lower().strip(); identifier=p.identifier.strip()
    if method=='email':
        try: EmailStr(identifier)
        except Exception: raise HTTPException(422,'Please enter a valid email address.')
    u=find_recovery_user(method,identifier,db)
    if not u: raise HTTPException(404,'No FinSight account was found with those details.')
    otp=str(secrets.randbelow(900000)+100000); reset_id=uid()
    db.password_resets.delete_many({'user_id':u['_id'],'verified':False})
    db.password_resets.insert_one({'_id':reset_id,'user_id':u['_id'],'method':method,'otp_hash':hash_otp(otp),'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat(),'attempts':0,'verified':False,'created_at':now()})
    delivered=False
    try:
        delivered=send_email_otp(u['email'],otp) if method=='email' else send_sms_otp(str(u.get('phone','')),otp)
    except Exception as exc:
        db.password_resets.delete_one({'_id':reset_id})
        if os.getenv('DEV_OTP_MODE','false').lower()!='true': raise HTTPException(503,f'Unable to send OTP: {exc}')
    response={'ok':True,'reset_id':reset_id,'destination':mask_email(u['email']) if method=='email' else mask_phone(str(u.get('phone',''))),'message':f'Verification OTP sent to your {method}.'}
    if not delivered:
        if os.getenv('DEV_OTP_MODE','false').lower()!='true':
            db.password_resets.delete_one({'_id':reset_id}); raise HTTPException(503,'OTP delivery is not configured. Configure email/SMS service first.')
        response['dev_otp']=otp; response['message']='Development OTP generated successfully.'
    return response

@app.post('/api/auth/forgot-password/verify-otp')
def forgot_password_verify_otp(p:ForgotPasswordVerifyOtpIn,db=Depends(get_db)):
    reset=db.password_resets.find_one({'_id':p.reset_id})
    if not reset: raise HTTPException(404,'Recovery session not found.')
    if reset.get('verified'): raise HTTPException(400,'OTP has already been verified.')
    if datetime.now(timezone.utc)>datetime.fromisoformat(reset['expires_at']): raise HTTPException(400,'OTP has expired. Please request a new OTP.')
    if int(reset.get('attempts',0))>=5: raise HTTPException(429,'Too many incorrect OTP attempts. Please request a new OTP.')
    if hash_otp(p.otp)!=reset['otp_hash']:
        db.password_resets.update_one({'_id':p.reset_id},{'$inc':{'attempts':1}}); raise HTTPException(400,'Incorrect OTP. Please try again.')
    reset_token=secrets.token_urlsafe(32)
    db.password_resets.update_one({'_id':p.reset_id},{'$set':{'verified':True,'verified_at':now(),'reset_token_hash':hash_reset_token(reset_token)}})
    return {'ok':True,'reset_token':reset_token,'message':'OTP verified successfully.'}

@app.post('/api/auth/forgot-password/reset')
def forgot_password_reset(p:ForgotPasswordResetIn,db=Depends(get_db)):
    reset=db.password_resets.find_one({'reset_token_hash':hash_reset_token(p.reset_token),'verified':True})
    if not reset: raise HTTPException(400,'Invalid or expired password reset session.')
    if datetime.now(timezone.utc)-datetime.fromisoformat(reset['verified_at'])>timedelta(minutes=15):
        db.password_resets.delete_one({'_id':reset['_id']}); raise HTTPException(400,'Password reset session has expired. Please start again.')
    u=db.users.find_one({'_id':reset['user_id']})
    if not u: raise HTTPException(404,'User account no longer exists.')
    db.users.update_one({'_id':u['_id']},{'$set':{'password_hash':hash_password(p.new_password),'updated_at':now()}})
    db.audit_logs.insert_one({'_id':uid(),'user_id':u['_id'],'action':'password_reset_otp','target':'user:'+u['_id'],'created_at':now()})
    db.password_resets.delete_one({'_id':reset['_id']})
    return {'ok':True,'message':'Password reset successfully. You can now sign in.'}

@app.get('/api/me')
def me(user=Depends(get_current_user)): return user_out(user)
@app.post('/api/requests')
def create_request(p:RequestIn,user=Depends(get_current_user),db=Depends(get_db)):
    r={'_id':uid(),'client_id':user['_id'],'business_name':p.business_name,'business_type':p.business_type,'period_from':p.period_from,'period_to':p.period_to,'requested_areas':p.requested_areas,'additional_info':p.additional_info,'status':'New','created_at':now(),'updated_at':now()}; db.requests.insert_one(r); db.audit_logs.insert_one({'_id':uid(),'user_id':user['_id'],'action':'create_request','target':'request:'+r['_id'],'created_at':now()}); return request_out(r,db)
@app.get('/api/requests')
def list_requests(user=Depends(get_current_user),db=Depends(get_db)):
    q={} if user['role']=='admin' else {'client_id':user['_id']}; return [request_out(r,db) for r in db.requests.find(q).sort('created_at',-1)]
@app.post('/api/requests/{request_id}/files')
async def upload_files(request_id:str,files:list[UploadFile]=File(...),user=Depends(get_current_user),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id});
    if not r or (user['role']!='admin' and r['client_id']!=user['_id']): raise HTTPException(404,'Request not found')
    results=[]
    for f in files:
        ext=Path(f.filename or '').suffix.lower()
        if ext not in ALLOWED: raise HTTPException(400,f'Unsupported file type: {ext}')
        data=await f.read()
        if len(data)>MAX_UPLOAD_MB*1024*1024: raise HTTPException(413,'File too large')
        stored=f'{uuid.uuid4().hex}{ext}'; path=UPLOAD_DIR/stored; path.write_bytes(data); row={'_id':uid(),'request_id':request_id,'original_name':f.filename,'stored_name':str(path),'content_type':f.content_type,'size':len(data),'created_at':now()}; db.files.insert_one(row); results.append({'id':row['_id'],'original_name':row['original_name'],'size':row['size'],'created_at':row['created_at']})
    db.audit_logs.insert_one({'_id':uid(),'user_id':user['_id'],'action':'upload_file','target':'request:'+request_id,'created_at':now()}); return {'files':results}
@app.get('/api/files/{file_id}')
def download_file(file_id:str,user=Depends(get_current_user),db=Depends(get_db)):
    f=db.files.find_one({'_id':file_id});
    if not f: raise HTTPException(404,'File not found')
    r=db.requests.find_one({'_id':f['request_id']})
    if user['role']!='admin' and r['client_id']!=user['_id']: raise HTTPException(403,'Forbidden')
    return FileResponse(f['stored_name'],filename=f['original_name'])
@app.post('/api/admin/requests/{request_id}/status')
def set_status(request_id:str,p:StatusIn,user=Depends(require_admin),db=Depends(get_db)):
    allowed={'New','Under Review','In Analysis','Internal Review','Report Ready','Completed'}
    if p.status not in allowed: raise HTTPException(400,'Invalid status')
    r=db.requests.find_one({'_id':request_id});
    if not r: raise HTTPException(404,'Request not found')
    db.requests.update_one({'_id':request_id},{'$set':{'status':p.status,'updated_at':now()}}); return request_out(db.requests.find_one({'_id':request_id}),db)
@app.post('/api/admin/requests/{request_id}/financials')
def update_financials(request_id:str,p:FinancialsIn,user=Depends(require_admin),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id})
    if not r: raise HTTPException(404,'Request not found')
    profit=p.profit if p.profit else p.revenue-p.expenses
    margin=p.margin if p.margin else ((profit/p.revenue*100) if p.revenue else 0)
    result={'revenue':p.revenue,'expenses':p.expenses,'profit':profit,'margin':margin,'expense_categories':p.expense_categories,'findings':p.findings or ['Review the largest expense categories and validate unusual movements.']}
    a={'_id':uid(),'request_id':request_id,**result,'created_at':now(),'source':'admin_entered'}
    db.analyses.insert_one(a)
    # Saving values immediately creates the client-ready PDF using the saved numbers.
    client=db.users.find_one({'_id':r['client_id']})
    content=build_report_content(r,a)
    stored=f'report_{request_id}_{uuid.uuid4().hex[:8]}.pdf'; report_path=REPORT_DIR/stored
    build_pdf(str(report_path),client['full_name'] if client else 'Client',r,a,content)
    rep={'_id':uid(),'request_id':request_id,'title':content['title'],'stored_name':str(report_path),'created_at':now(),'content':content,'analysis_id':a['_id'],'status':'Ready'}
    db.reports.insert_one(rep)
    db.requests.update_one({'_id':request_id},{'$set':{'status':'Report Ready','updated_at':now(),'financials_entered':True}})
    return {**analysis_out(a),'report':{'id':rep['_id'],'title':rep['title'],'status':'Ready'}}

@app.post('/api/admin/requests/{request_id}/upload-and-analyze')
async def admin_upload_and_analyze(request_id:str,file:UploadFile=File(...),user=Depends(require_admin),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id})
    if not r: raise HTTPException(404,'Request not found')
    ext=Path(file.filename or '').suffix.lower()
    if ext not in {'.xlsx','.xlsm','.xls','.csv'}: raise HTTPException(400,'Please upload an Excel or CSV financial file.')
    data=await file.read()
    if len(data)>MAX_UPLOAD_MB*1024*1024: raise HTTPException(413,'File too large')
    stored=f'{uuid.uuid4().hex}{ext}'; path=UPLOAD_DIR/stored; path.write_bytes(data)
    row={'_id':uid(),'request_id':request_id,'original_name':file.filename,'stored_name':str(path),'content_type':file.content_type,'size':len(data),'created_at':now(),'source':'admin_report_upload'}
    db.files.insert_one(row)
    try: result=analyze_files([row])
    except ValueError as e: raise HTTPException(400,str(e))
    a={'_id':uid(),'request_id':request_id,**result,'created_at':now(),'source':'excel_upload','source_file':file.filename}
    db.analyses.insert_one(a)
    client=db.users.find_one({'_id':r['client_id']})
    content=build_report_content(r,a)
    stored_report=f'report_{request_id}_{uuid.uuid4().hex[:8]}.pdf'; report_path=REPORT_DIR/stored_report
    build_pdf(str(report_path),client['full_name'] if client else 'Client',r,a,content)
    rep={'_id':uid(),'request_id':request_id,'title':content['title'],'stored_name':str(report_path),'created_at':now(),'content':content,'analysis_id':a['_id'],'status':'Draft','source_file':file.filename}
    db.reports.insert_one(rep)
    db.requests.update_one({'_id':request_id},{'$set':{'status':'Internal Review','updated_at':now(),'financials_entered':True}})
    return {'file':{'id':row['_id'],'name':row['original_name'],'size':row['size']},'analysis':analysis_out(a),'report':{'id':rep['_id'],'title':rep['title'],'status':'Draft'}}

@app.post('/api/admin/requests/{request_id}/analyze')
def run_analysis(request_id:str,user=Depends(require_admin),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id});
    if not r: raise HTTPException(404,'Request not found')
    try:
        result=analyze_files(list(db.files.find({'request_id':request_id})))
    except ValueError as e:
        demo=r.get('demo_analysis')
        if not demo: raise HTTPException(400,str(e))
        result=demo.copy()
    a={'_id':uid(),'request_id':request_id,**result,'created_at':now()}; db.analyses.insert_one(a)
    client=db.users.find_one({'_id':r['client_id']})
    content=build_report_content(r,a)
    stored=f'report_{request_id}_{uuid.uuid4().hex[:8]}.pdf'; path=REPORT_DIR/stored
    build_pdf(str(path),client['full_name'] if client else 'Client',r,a,content)
    rep={'_id':uid(),'request_id':request_id,'title':content['title'],'stored_name':str(path),'created_at':now(),'content':content,'analysis_id':a['_id'],'status':'Ready','source':'analysis_page'}
    db.reports.insert_one(rep)
    db.requests.update_one({'_id':request_id},{'$set':{'status':'Report Ready','updated_at':now(),'financials_entered':True}})
    return {**analysis_out(a),'report':{'id':rep['_id'],'title':rep['title'],'status':'Ready'}}
def build_report_content(request, analysis):
    business=request.get("business_name","Business")
    return {
        "title":f"Financial Analysis Report — {business}",
        "executive_summary":f"{business} has a net margin of {float(analysis.get('margin',0)):.1f}%. This report summarizes profitability, cost drivers and practical opportunities for improvement.",
        "findings":analysis.get("findings",[]),
        "recommendations":["Review the largest cost categories monthly.","Compare budget versus actual performance.","Review pricing and contribution margins.","Monitor operating cash requirements alongside profit.","Re-run the analysis after the next reporting period."],
        "analyst_notes":"",
        "case_study":{
            "option_a":{"name":"Option A","advantages":["No ownership dilution","Tax shield on interest","Lower WACC","Higher EPS if project succeeds"],"disadvantages":["Interest coverage drops to risky levels","Fixed obligation even if project delayed"]},
            "option_b":{"name":"Option B","advantages":["Much lower leverage (D/E = 0.25)","Better interest coverage (>2.0×)","PE brings governance & expertise"],"disadvantages":["11.6% ownership dilution","PE gets board seats & tag-along rights","Higher WACC"]},
            "final_decision":"Option B",
            "considering":"Fixed obligation, NPV sensitivity, Competitive Market, Project Delay, Better Interest Coverage"
        }
    }

def analysis_out(a): return {'id':a['_id'],'revenue':a['revenue'],'expenses':a['expenses'],'profit':a['profit'],'margin':a['margin'],'expense_categories':a.get('expense_categories',{}),'findings':a.get('findings',[]),'created_at':a['created_at']}
@app.get('/api/requests/{request_id}/analysis')
def get_analysis(request_id:str,user=Depends(get_current_user),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id});
    if not r or (user['role']!='admin' and r['client_id']!=user['_id']): raise HTTPException(404,'Request not found')
    a=db.analyses.find_one({'request_id':request_id},sort=[('created_at',-1)])
    if not a: raise HTTPException(404,'Analysis not available')
    return analysis_out(a)
@app.post('/api/admin/requests/{request_id}/generate-report')
def generate_report(request_id:str,user=Depends(require_admin),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id}); a=db.analyses.find_one({'request_id':request_id},sort=[('created_at',-1)])
    if not r or not a: raise HTTPException(400,'Run or upload an analysis first')
    client=db.users.find_one({'_id':r['client_id']})
    if not client: raise HTTPException(404,'Client not found')
    content=build_report_content(r,a)
    stored=f'report_{request_id}_{uuid.uuid4().hex[:8]}.pdf'; path=REPORT_DIR/stored
    build_pdf(str(path),client['full_name'],r,a,content)
    rep={'_id':uid(),'request_id':request_id,'title':content['title'],'stored_name':str(path),'created_at':now(),'content':content,'analysis_id':a['_id'],'status':'Ready'}
    db.reports.insert_one(rep); db.requests.update_one({'_id':request_id},{'$set':{'status':'Report Ready','updated_at':now()}})
    return {'id':rep['_id'],'title':rep['title'],'created_at':rep['created_at']}

@app.get('/api/admin/reports/{report_id}')
def admin_report_detail(report_id:str,user=Depends(require_admin),db=Depends(get_db)):
    rep=db.reports.find_one({'_id':report_id})
    if not rep: raise HTTPException(404,'Report not found')
    r=db.requests.find_one({'_id':rep['request_id']}); a=db.analyses.find_one({'_id':rep.get('analysis_id')}) if rep.get('analysis_id') else db.analyses.find_one({'request_id':rep['request_id']},sort=[('created_at',-1)])
    return {'id':rep['_id'],'title':rep['title'],'created_at':rep['created_at'],'sent_at':rep.get('sent_at'),'content':rep.get('content',{}),'analysis':analysis_out(a) if a else None,'business_name':r.get('business_name','') if r else ''}

@app.put('/api/admin/reports/{report_id}')
def edit_report(report_id:str,p:ReportEditIn,user=Depends(require_admin),db=Depends(get_db)):
    rep=db.reports.find_one({'_id':report_id})
    if not rep: raise HTTPException(404,'Report not found')
    content=p.model_dump(); r=db.requests.find_one({'_id':rep['request_id']}); a=db.analyses.find_one({'_id':rep.get('analysis_id')}) if rep.get('analysis_id') else db.analyses.find_one({'request_id':rep['request_id']},sort=[('created_at',-1)])
    client=db.users.find_one({'_id':r['client_id']}) if r else None
    if not r or not a or not client: raise HTTPException(400,'Report source data is unavailable')
    build_pdf(rep['stored_name'],client['full_name'],r,a,content)
    db.reports.update_one({'_id':report_id},{'$set':{'title':content['title'],'content':content,'updated_at':now(),'status':('Delivered' if rep.get('sent_at') else 'Ready')}})
    return {'ok':True,'id':report_id,'content':content}

@app.delete('/api/admin/reports/{report_id}')
def delete_report(report_id:str,user=Depends(require_admin),db=Depends(get_db)):
    rep=db.reports.find_one({'_id':report_id})
    if not rep: raise HTTPException(404,'Report not found')
    try: Path(rep.get('stored_name','')).unlink(missing_ok=True)
    except Exception: pass
    db.reports.delete_one({'_id':report_id}); return {'ok':True}

@app.post('/api/admin/reports/{report_id}/send')
def send_report(report_id:str,user=Depends(require_admin),db=Depends(get_db)):
    rep=db.reports.find_one({'_id':report_id})
    if not rep: raise HTTPException(404,'Report not found')
    r=db.requests.find_one({'_id':rep['request_id']})
    if not r: raise HTTPException(404,'Request not found')
    client=db.users.find_one({'_id':r['client_id']})
    if not client: raise HTTPException(404,'Client not found')
    sent=now(); db.reports.update_one({'_id':report_id},{'$set':{'sent_at':sent,'sent_by':user['_id'],'status':'Delivered'}})
    db.requests.update_one({'_id':r['_id']},{'$set':{'status':'Completed','updated_at':sent}})
    db.messages.insert_one({'_id':uid(),'request_id':r['_id'],'sender_id':user['_id'],'body':f'Your FinSight financial analysis report "{rep["title"]}" is now ready in My Reports.','created_at':sent,'message_type':'report_delivery','report_id':report_id})
    return {'ok':True,'message':'Report sent to client','sent_at':sent,'client_name':client.get('full_name','')}

@app.get('/api/reports/{report_id}/download')
def download_report(report_id:str,user=Depends(get_current_user),db=Depends(get_db)):
    rep=db.reports.find_one({'_id':report_id});
    if not rep: raise HTTPException(404,'Report not found')
    r=db.requests.find_one({'_id':rep['request_id']})
    if user['role']!='admin' and r['client_id']!=user['_id']: raise HTTPException(403,'Forbidden')
    return FileResponse(rep['stored_name'],filename=os.path.basename(rep['stored_name']),media_type='application/pdf')
@app.get('/api/messages/{request_id}')
def messages(request_id:str,user=Depends(get_current_user),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id});
    if not r or (user['role']!='admin' and r['client_id']!=user['_id']): raise HTTPException(404,'Request not found')
    out=[]
    for m in db.messages.find({'request_id':request_id}).sort('created_at',1):
        s=db.users.find_one({'_id':m['sender_id']}); out.append({'id':m['_id'],'sender_id':m['sender_id'],'sender_name':s['full_name'],'body':m['body'],'created_at':m['created_at']})
    return out
@app.post('/api/messages/{request_id}')
def send_message(request_id:str,p:MessageIn,user=Depends(get_current_user),db=Depends(get_db)):
    r=db.requests.find_one({'_id':request_id});
    if not r or (user['role']!='admin' and r['client_id']!=user['_id']): raise HTTPException(404,'Request not found')
    m={'_id':uid(),'request_id':request_id,'sender_id':user['_id'],'body':p.body,'created_at':now()}; db.messages.insert_one(m); return {'id':m['_id'],'sender_id':m['sender_id'],'sender_name':user['full_name'],'body':m['body'],'created_at':m['created_at']}
@app.get('/api/admin/clients')
def admin_clients(user=Depends(require_admin),db=Depends(get_db)):
    return [{'id':u['_id'],'full_name':u.get('full_name',''),'username':u.get('username',''),'business_name':u.get('business_name',''),'email':u.get('email',''),'phone':u.get('phone',''),'business_type':u.get('business_type',''),'created_at':u.get('created_at','')} for u in db.users.find({'role':'client'}).sort('created_at',-1)]

@app.get('/api/admin/stats')
def admin_stats(user=Depends(require_admin),db=Depends(get_db)): return {'clients':db.users.count_documents({'role':'client'}),'requests':db.requests.count_documents({}),'in_analysis':db.requests.count_documents({'status':'In Analysis'}),'reports_ready':db.requests.count_documents({'status':'Report Ready'})}

class ContactIn(BaseModel): full_name:str; business_name:str=''; email:EmailStr; phone:str=''; message:str
@app.post('/api/contact')
def contact(p:ContactIn,db=Depends(get_db)):
    row={'_id':uid(),**p.model_dump(),'created_at':now(),'status':'New'}; db.contact_inquiries.insert_one(row); return {'ok':True,'message':'Thanks. FinSight will contact you shortly.'}

@app.get('/api/admin/contact-inquiries')
def admin_contact_inquiries(db=Depends(get_db),admin=Depends(require_admin)):
    rows=list(db.contact_inquiries.find().sort('created_at',-1))
    return [{'id':r['_id'],'full_name':r.get('full_name',''),'business_name':r.get('business_name',''),'email':r.get('email',''),'phone':r.get('phone',''),'message':r.get('message',''),'created_at':r.get('created_at',''),'status':r.get('status','New')} for r in rows]

class ContactStatusIn(BaseModel):
    status:str=Field(pattern='^(New|In Progress|Replied|Archived)$')

@app.post('/api/admin/contact-inquiries/{inquiry_id}/status')
def update_contact_status(inquiry_id:str,p:ContactStatusIn,db=Depends(get_db),admin=Depends(require_admin)):
    result=db.contact_inquiries.update_one({'_id':inquiry_id},{'$set':{'status':p.status,'updated_at':now()}})
    if result.matched_count==0: raise HTTPException(404,'Contact inquiry not found')
    return {'ok':True,'status':p.status}
