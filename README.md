# FinSight Analytics — Full Stack MVP

A production-minded MVP for FinSight Analytics with a dark teal/black UI, client portal, admin portal, authentication, file uploads, reports, messaging, and a Python financial-analysis engine.

## Stack
- Frontend: React + Vite + React Router + Lucide React
- Backend: FastAPI + SQLAlchemy
- Database: SQLite by default (easy local setup); can be changed to PostgreSQL with `DATABASE_URL`
- Storage: private local folders for uploads/reports; swap to S3-compatible storage later
- Analysis: pandas + openpyxl
- PDF reports: ReportLab
- Passwords: Python `hashlib.scrypt`
- Auth: signed HTTP-style bearer tokens using `itsdangerous`

## Features
### Public
Home, How It Works, Services, Contact, Login, Register.

### Client
Dashboard, My Requests, Submit Data, My Reports, Messages, Profile, Logout.

### Admin
Dashboard, Clients, Requests, Analysis workspace, Reports, Messages, Logout.

### Backend
- Real signup/login against database
- Admin-only authentication and authorization
- Client data isolation
- Secure private file download endpoints
- CSV/XLSX analysis
- Automated financial summary + PDF report generation
- Client/admin messaging
- Request status workflow
- Audit log table

## Quick start

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
python seed_admin.py
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

Default seeded admin (change immediately):
- Email: `admin@finsight.local`
- Password: `ChangeMe123!`

### 2. Frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

The frontend uses `/api` and Vite proxies that to FastAPI.

## Production checklist
- Use PostgreSQL
- Use S3/Cloud storage for private files
- Put app behind HTTPS
- Set a strong `SECRET_KEY`
- Rotate admin credentials
- Add email verification/password reset
- Add rate limiting and CSRF protection if switching to cookie auth
- Add antivirus scanning for uploaded files
- Add object-level authorization tests
- Configure backups, monitoring and audit retention

## MongoDB setup
This version uses MongoDB instead of SQLite/SQLAlchemy. Set `MONGODB_URL` and `MONGODB_DB` in `backend/.env`. Local default: `mongodb://127.0.0.1:27017`, database `finsight`.
Run `python seed_admin.py` from the backend folder after MongoDB is running.

Collections used: `users`, `requests`, `files`, `analyses`, `reports`, `messages`, `audit_logs`.

## FinSight Report Factory (v4)

The Admin portal now supports an end-to-end report workflow:

1. **Create Report** — select a client business and upload `.xlsx`, `.xlsm`, `.xls` or `.csv` data.
2. **Automatic processing** — the backend reads common revenue, sales, expense, cost and profit fields with pandas and calculates margin and cost structure.
3. **Draft report** — a branded FinSight PDF is created automatically and stored as a draft.
4. **Edit Report** — Admin can edit the report title, executive summary, findings, recommendations and analyst notes. Saving edits regenerates the PDF.
5. **Report Management** — search/filter reports, preview details, view PDF, download PDF and delete reports.
6. **Send to Client** — sending marks the report Delivered, completes the request and creates a client message.
7. **Client Report Center** — clients only see reports after delivery and can open an understandable financial summary before downloading the full PDF.

### Admin workflow
`Admin → Create Report → Select Business → Upload Excel → Process → Reports → Edit → Download/View → Send to Client`

### Supported Excel conventions
The processor detects common columns such as `Revenue`, `Sales`, `Income`, `Expenses`, `Expense`, `Cost`, `Total Cost`, and `Profit` / `Net Profit`. Expense/cost columns are also used to build the report cost structure.


## V6 UI Design
The Admin and Client portals were visually refreshed to follow the supplied FinSight mockup: dark navy fintech workspace, teal active navigation, compact KPI cards, command-center panels, business/report tables, secure client workspace, and responsive layouts. The supplied mockup is included at `docs/ui-reference-admin-client.png` as a visual reference.


## V7 updates
- Redesigned Client Submit Data form with larger professional fields and circular goal checks.
- Redesigned Admin financial input section.
- Added new professional landing page.
- Added Forgot Password flow with email + Indian phone validation and password reset.
- Fixed notification button with a functional notification dropdown.
- Fixed user id output so frontend user identity works correctly.
- Added Vercel SPA rewrite and `VITE_API_URL` support for production.

### Local run
Backend: `cd backend`, activate your virtual environment, `python -m pip install -r requirements.txt`, then `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
Frontend: `cd frontend`, `npm install`, then `npm run dev`

### Production
Set `VITE_API_URL` to your deployed FastAPI backend URL in Vercel. Set `MONGODB_URL`, `MONGODB_DB`, `SECRET_KEY`, and `CORS_ORIGINS` on the backend host.

## V7 deployment
See `DEPLOYMENT_GUIDE.md` for complete local run, MongoDB Atlas, Render, Vercel, environment-variable, seeding and production security instructions.
