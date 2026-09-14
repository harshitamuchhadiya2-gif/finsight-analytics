from app.db.session import db
from app.core.security import hash_password
from datetime import datetime, timezone
import uuid, random

def uid(): return uuid.uuid4().hex
def now(): return datetime.now(timezone.utc).isoformat()
def growth(base_rev, margin, months=6):
    out=[]
    for i,m in enumerate(['Apr','May','Jun','Jul','Aug','Sep']):
        rev=round(base_rev*(1+i*random.uniform(.025,.055)))
        exp=round(rev*(1-margin-random.uniform(.005,.018)))
        profit=rev-exp
        out.append({'month':m,'revenue':rev,'expenses':exp,'profit':profit,'margin':profit/rev*100})
    return out

# Create or refresh the demo administrator. Change this password before production use.
admin_email='admin@finsight.local'; admin_username='admin'
admin=db.users.find_one({'$or':[{'email':admin_email},{'username':admin_username}]})
if not admin:
    db.users.insert_one({'_id':'admin','full_name':'FinSight Administrator','username':admin_username,'business_name':'FinSight Analytics','email':admin_email,'phone':'9876500000','business_type':'Financial Analysis','password_hash':hash_password('ChangeMe123!'),'role':'admin','created_at':now()})

businesses=[
('Rahul Patel','rahulmetal','rahul@demo.finsight.local','Patel Metal Works','Metal Manufacturing','9876501001',4800000,.13),
('Neha Shah','neharestaurant','neha@demo.finsight.local','Urban Spice Restaurant','Restaurant','9876501002',1650000,.12),
('Amit Mehta','amitfashion','amit@demo.finsight.local','Mehta Fashion Hub','Retail / Fashion','9876501003',2200000,.11),
('Priya Desai','priyaelectronics','priya@demo.finsight.local','Desai Electronics Distribution','Electronics Distribution','9876501004',3100000,.095),
('Kunal Shah','kunalauto','kunal@demo.finsight.local','Shah Auto Components','Automotive Manufacturing','9876501005',4200000,.14),
('Riya Joshi','riyafoods','riya@demo.finsight.local','GreenLeaf Foods','Food Manufacturing','9876501006',2750000,.105),
('Dhruv Patel','dhruvfurniture','dhruv@demo.finsight.local','Sunrise Furniture Works','Furniture Manufacturing','9876501007',1950000,.13),
('Anjali Mehta','anjalpharma','anjali@demo.finsight.local','Prime Pharma Distributors','Healthcare Distribution','9876501008',3600000,.085),
('Vivek Shah','viveklogistics','vivek@demo.finsight.local','BlueWave Logistics','Logistics & Transport','9876501009',2400000,.10),
('Sonal Desai','sonalconstruction','sonal@demo.finsight.local','Royal Construction Materials','Construction Supply','9876501010',5200000,.09),
('Harsh Patel','harshtextile','harsh@demo.finsight.local','Ahmedabad Textile Traders','Textile Trading','9876501011',3350000,.115),
('Nisha Shah','nishatech','nisha@demo.finsight.local','SmartTech Solutions','IT Services','9876501012',1850000,.18),
('Manav Mehta','manavfreshmart','manav@demo.finsight.local','FreshMart Wholesale','Wholesale','9876501013',4100000,.075),
('Pooja Joshi','poojapackaging','pooja@demo.finsight.local','Krishna Packaging Industries','Packaging Manufacturing','9876501014',2950000,.125),
('Arjun Desai','arjunelectricals','arjun@demo.finsight.local','Silverline Electricals','Electrical Manufacturing','9876501015',3900000,.135),
]
statuses=['Under Review','In Analysis','New','Report Ready','Completed']
for idx,(name,uname,email,biz,typ,phone,base,margin) in enumerate(businesses):
    u=db.users.find_one({'$or':[{'email':email},{'username':uname}]})
    if not u:
        uidv=uid(); u={'_id':uidv,'full_name':name,'username':uname,'business_name':biz,'email':email,'phone':phone,'business_type':typ,'password_hash':hash_password('Demo@12345'),'role':'client','created_at':now()}; db.users.insert_one(u)
    rid='demo-'+uname
    g=growth(base,margin)
    latest=g[-1]
    demo={'revenue':latest['revenue'],'expenses':latest['expenses'],'profit':latest['profit'],'margin':latest['margin'],
          'expense_categories':{'Raw Materials / Direct Costs':round(latest['expenses']*.52),'Labour / Salaries':round(latest['expenses']*.16),'Operations':round(latest['expenses']*.12),'Logistics / Utilities':round(latest['expenses']*.10),'Other Expenses':round(latest['expenses']*.10)},
          'findings':[f'{biz} shows a {g[-1]["margin"]:.1f}% latest net margin.', 'Review the largest cost category monthly and compare supplier or operating rates.', 'Use monthly revenue and profit trends to plan pricing and cash requirements.']}
    r=db.requests.find_one({'_id':rid})
    if not r:
        r={'_id':rid,'client_id':u['_id'],'business_name':biz,'business_type':typ,'period_from':'2026-04','period_to':'2026-09',
           'requested_areas':['Revenue','Expenses','Profitability','Cash Flow','Overall Performance'],'additional_info':'Demo portfolio business for FinSight testing.',
           'status':statuses[idx%len(statuses)],'created_at':now(),'updated_at':now(),'growth':g,'summary':demo,'demo_analysis':demo}
        db.requests.insert_one(r)
    else:
        db.requests.update_one({'_id':rid},{'$set':{'growth':g,'summary':demo,'demo_analysis':demo}})
    if not db.analyses.find_one({'request_id':rid}):
        db.analyses.insert_one({'_id':uid(),'request_id':rid,**demo,'created_at':now()})
    if not db.messages.find_one({'request_id':rid}):
        db.messages.insert_many([
          {'_id':uid(),'request_id':rid,'sender_id':u['_id'],'body':f'Hello FinSight team, can you explain the main cost driver for {biz}?','created_at':now()},
          {'_id':uid(),'request_id':rid,'sender_id':'admin','body':'Absolutely. We are reviewing the cost mix and will share a clear recommendation in the analysis report.','created_at':now()}
        ])
print(f'Demo portfolio ready: {len(businesses)} businesses')
print('Client password for all demo accounts: Demo@12345')
