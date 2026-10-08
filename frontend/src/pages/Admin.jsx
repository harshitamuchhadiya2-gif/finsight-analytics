import {useEffect,useMemo,useState} from 'react';
import {Link} from 'react-router-dom';
import PortalShell from '../components/PortalShell';
import {api,download,openPdf} from '../lib/api';
import {
  Users,FileText,TrendingUp,Wallet,MessageSquare,Download,Send,Save,
  RefreshCw,ShieldCheck,ArrowUpRight,Activity,UploadCloud,Eye,Trash2,
  Edit3,FileSpreadsheet,CheckCircle2,Clock3,BarChart3,Paperclip,
  Building2,HelpCircle,Layers,ChevronRight,AlertCircle,FileCheck,FileDown
} from 'lucide-react';

const money = n => '₹' + Number(n || 0).toLocaleString('en-IN', {maximumFractionDigits: 0});
const pct = n => Number(n || 0).toFixed(1) + '%';
const date = d => d ? new Date(d).toLocaleDateString('en-IN', {day: '2-digit', month: 'short', year: 'numeric'}) : '—';
const formatBytes = b => {
  const bytes = Number(b || 0);
  if (!bytes) return '—';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
};

function K({title, value, text, icon: I}) {
  return (
    <div className="kpi kpi-rich">
      <div className="kpi-icon"><I/></div>
      <small>{title}</small>
      <strong>{value}</strong>
      <span>{text}</span>
    </div>
  );
}

export default function Admin({view='dashboard'}) {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('finsight_user') || 'null'));
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState({});
  const [clients, setClients] = useState([]);
  const [notice, setNotice] = useState('');

  async function refresh() {
    const [r, s, c] = await Promise.all([api.requests(), api.stats(), api.clients()]);
    setRequests(r);
    setStats(s);
    setClients(c);
  }

  useEffect(() => {
    api.me().then(setUser).catch(() => {});
    refresh().catch(e => setNotice(e.message));
  }, []);

  const shell = c => (
    <PortalShell admin user={user}>
      {c}
      {notice && <div className="success page-message">{notice}</div>}
    </PortalShell>
  );

  if (view === 'requests') return shell(<Requests requests={requests}/>);
  if (view === 'analysis') return shell(<Analysis requests={requests} refresh={refresh}/>);
  if (view === 'create-report') return shell(<CreateReport requests={requests} refresh={refresh}/>);
  if (view === 'clients') return shell(<Clients clients={clients} requests={requests}/>);
  if (view === 'reports') return shell(<Reports requests={requests} refresh={refresh}/>);
  if (view === 'messages') return shell(<Messages requests={requests} user={user}/>);
  if (view === 'contact-inquiries') return shell(<ContactInquiries/>);
  if (view === 'profile') return shell(<Profile user={user}/>);
  return shell(<Dashboard stats={stats} requests={requests}/>);
}

function Dashboard({stats, requests}) {
  const ready = requests.filter(r => r.status === 'Report Ready').length;
  const completed = requests.filter(r => r.status === 'Completed').length;

  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">FINSIGHT OPERATIONS</p>
          <h1>Business Command Center</h1>
          <p>Review client submissions, download original reports, calculate financial analyses, and deliver executive advisory reports.</p>
        </div>
        <div className="dash-head-actions">
          <Link className="btn" to="/admin/create-report"><UploadCloud size={16}/> Create Report</Link>
        </div>
      </div>

      <div className="kpis">
        <K title="Clients" value={stats.clients || 0} text="Registered corporate accounts" icon={Users}/>
        <K title="Active Requests" value={(stats.requests || 0) - completed} text="Engagements in progress" icon={Activity}/>
        <K title="Reports Ready" value={ready} text="Awaiting delivery" icon={FileText}/>
        <K title="Completed" value={completed} text="Delivered engagements" icon={ShieldCheck}/>
      </div>

      <div className="admin-command-grid">
        <div className="admin-command">
          <p className="eyebrow">REPORT FACTORY</p>
          <h2>From Client Data to Executive Advisory</h2>
          <p>Download the client's original Excel/PDF dataset, run FinSight financial extraction, customize strategic recommendations, and issue branded reports.</p>
          <div className="factory-steps">
            <span><b>01</b> Original Data</span>
            <span><b>02</b> Calculate</span>
            <span><b>03</b> Edit & Polish</span>
            <span><b>04</b> Client Delivery</span>
          </div>
          <Link className="btn small" to="/admin/create-report">Start report workflow →</Link>
        </div>
        <div className="panel">
          <p className="eyebrow">DELIVERY QUEUE</p>
          <strong className="admin-value">{ready}</strong>
          <p>reports are ready for final executive delivery.</p>
          <Link className="text-action" to="/admin/reports">Open report management →</Link>
        </div>
      </div>

      <div className="panel">
        <div className="panel-title">
          <h2>Recent Client Activity</h2>
          <Link to="/admin/requests">View all requests →</Link>
        </div>
        <div className="recent-activity-list">
          {requests.slice(0, 8).map(r => (
            <div className="report-row responsive-activity-row" key={r.id}>
              <div>
                <b>{r.business_name}</b>
                <small>{r.client_name} · {r.business_type} · {r.files?.length || 0} file(s)</small>
              </div>
              <span className="status">{r.status}</span>
              <div className="row-inline-actions">
                {r.files?.length > 0 ? (
                  <button
                    className="btn-download-pill"
                    title={`Download original file sent by client: ${r.files[0].original_name}`}
                    onClick={() => download(`/files/${r.files[0].id}`, r.files[0].original_name)}
                  >
                    <Download size={13}/> Original File
                  </button>
                ) : (
                  <span className="no-file-pill"><FileText size={12}/> No file</span>
                )}
                <Link
                  className="btn small"
                  to="/admin/analysis"
                  onClick={() => localStorage.setItem('finsight_selected_request', r.id)}
                >
                  Analyze
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Requests({requests}) {
  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">CLIENT ENGAGEMENTS</p>
          <h1>Business Requests</h1>
          <p>Inspect client submissions, download original reports sent by clients, and initiate financial analyses.</p>
        </div>
      </div>

      <div className="panel portfolio-table responsive-portfolio-table">
        <div className="table-head req-table-head">
          <span>Business & Industry</span>
          <span>Client Details</span>
          <span>Reporting Period</span>
          <span>Status</span>
          <span>Original Report Sent by Client</span>
          <span>Action</span>
        </div>

        {requests.map(r => (
          <div className="table-row req-table-row" key={r.id}>
            <div className="row-business">
              <b>{r.business_name}</b>
              <small>{r.business_type || 'Corporate'}</small>
            </div>

            <div className="row-client">
              <span>{r.client_name}</span>
              <small>{r.client_email}</small>
            </div>

            <div className="row-period">
              <span>{r.period_from || '—'} → {r.period_to || '—'}</span>
            </div>

            <div className="row-status">
              <span className="status">{r.status}</span>
            </div>

            <div className="row-client-file">
              {r.files && r.files.length > 0 ? (
                <div className="client-file-actions-wrap">
                  {r.files.map((f, idx) => (
                    <button
                      key={f.id || idx}
                      className="btn-download-original"
                      title={`Download original file sent by client: ${f.original_name} (${formatBytes(f.size)})`}
                      onClick={() => download(`/files/${f.id}`, f.original_name)}
                    >
                      <Download size={14}/>
                      <span className="file-truncate" title={f.original_name}>{f.original_name}</span>
                      <small className="file-sz-pill">{formatBytes(f.size)}</small>
                    </button>
                  ))}
                </div>
              ) : (
                <span className="no-file-badge"><AlertCircle size={12}/> No client file attached</span>
              )}
            </div>

            <div className="row-open">
              <Link
                className="btn small"
                to="/admin/analysis"
                onClick={() => localStorage.setItem('finsight_selected_request', r.id)}
              >
                Analyze →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Analysis({requests, refresh}) {
  const initial = localStorage.getItem('finsight_selected_request');
  const [rid, setRid] = useState(initial || requests[0]?.id || null);
  const [a, setA] = useState(null);
  const [form, setForm] = useState({revenue: '', expenses: '', profit: '', margin: '', categories: '', findings: ''});
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  const r = requests.find(x => x.id === rid);

  useEffect(() => {
    if (!r) return;
    api.analysis(r.id)
      .then(x => {
        setA(x);
        setForm({
          revenue: x.revenue || '',
          expenses: x.expenses || '',
          profit: x.profit || '',
          margin: x.margin || '',
          categories: Object.entries(x.expense_categories || {}).map(([k, v]) => `${k}: ${v}`).join('\n'),
          findings: (x.findings || []).join('\n')
        });
      })
      .catch(() => setA(null));
  }, [rid]);

  const set = (k, v) => setForm(f => ({...f, [k]: v}));

  function computed() {
    const revenue = Number(form.revenue) || 0;
    const expenses = Number(form.expenses) || 0;
    const profit = form.profit !== '' ? Number(form.profit) : revenue - expenses;
    const margin = form.margin !== '' ? Number(form.margin) : (revenue ? (profit / revenue * 100) : 0);
    return {revenue, expenses, profit, margin};
  }

  async function save() {
    if (!r) return;
    setBusy(true);
    try {
      const c = computed();
      const cats = {};
      form.categories.split('\n').forEach(line => {
        const i = line.indexOf(':');
        if (i > 0) cats[line.slice(0, i).trim()] = Number(line.slice(i + 1).replace(/[^0-9.-]+/g, '')) || 0;
      });
      const x = await api.updateFinancials(r.id, {
        ...c,
        expense_categories: cats,
        findings: form.findings.split('\n').map(x => x.trim()).filter(Boolean)
      });
      setA(x);
      await refresh();
      setMessage(x.report ? 'Financial metrics saved and executive report successfully created.' : 'Financial values updated.');
    } catch (e) {
      setMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function auto() {
    setBusy(true);
    try {
      const x = await api.analyze(r.id);
      setA(x);
      setForm({
        revenue: x.revenue,
        expenses: x.expenses,
        profit: x.profit,
        margin: x.margin,
        categories: Object.entries(x.expense_categories || {}).map(([k, v]) => `${k}: ${v}`).join('\n'),
        findings: (x.findings || []).join('\n')
      });
      await refresh();
      setMessage(x.report ? 'Analysis calculated from uploaded dataset and report is ready.' : 'Analysis calculated from uploaded data.');
    } catch (e) {
      setMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (!r) {
    return (
      <section className="dash">
        <h1>Financial Workspace</h1>
        <div className="empty">No client requests available.</div>
      </section>
    );
  }

  const c = computed();

  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">FINANCIAL ANALYSIS WORKSPACE</p>
          <h1>{r.business_name}</h1>
          <p>{r.client_name} · {r.business_type} · Period: {r.period_from || '—'} to {r.period_to || '—'}</p>
        </div>
        <div className="analysis-toolbar">
          {r.files && r.files.length > 0 ? (
            <button
              className="btn btn-download-primary"
              title="Download the original report / dataset submitted by the client"
              onClick={() => download(`/files/${r.files[0].id}`, r.files[0].original_name)}
            >
              <Download size={15}/> Download Client Original Report
            </button>
          ) : (
            <button className="btn secondary" disabled title="No file uploaded by client">
              <Download size={15}/> No Client File
            </button>
          )}
          <button className="btn secondary" onClick={auto} disabled={busy}><RefreshCw size={15}/> Calculate from Data</button>
          <button className="btn" onClick={save} disabled={busy}><Save size={15}/> Save & Build Report</button>
          <Link className="btn secondary" to="/admin/create-report">Create / Upload Excel</Link>
          {(a?.report || r.reports?.length) && (
            <button
              className="btn secondary"
              onClick={() => {
                const rep = a?.report || r.reports[r.reports.length - 1];
                download(`/reports/${rep.id}/download`, safeName(rep.title) + '.pdf');
              }}
            >
              <Download size={15}/> Download Created Report
            </button>
          )}
        </div>
      </div>

      <div className="client-switcher panel">
        <div>
          <b>Selected Business Engagement</b>
          <small>Switch between client businesses to inspect their data and configure reports.</small>
        </div>
        <select
          value={rid || ''}
          onChange={e => {
            setRid(e.target.value);
            localStorage.setItem('finsight_selected_request', e.target.value);
          }}
        >
          {requests.map(x => (
            <option value={x.id} key={x.id}>
              {x.business_name} — {x.client_name} ({x.files?.length || 0} file{x.files?.length === 1 ? '' : 's'})
            </option>
          ))}
        </select>
      </div>

      {/* Prominent Client Uploaded File Card */}
      <div className="panel client-original-doc-card">
        <div className="client-doc-head">
          <div className="doc-icon"><FileSpreadsheet size={22}/></div>
          <div className="doc-meta">
            <span className="eyebrow">CLIENT SUBMITTED DOCUMENTATION</span>
            <h3>Original Financial Report Sent by Client</h3>
            <p>Original file received directly from {r.client_name} for {r.business_name}.</p>
          </div>
          <div className="doc-action">
            {r.files && r.files.length > 0 ? (
              <div className="doc-downloads-group">
                {r.files.map(f => (
                  <button
                    key={f.id}
                    className="btn download-client-file-btn"
                    onClick={() => download(`/files/${f.id}`, f.original_name)}
                  >
                    <Download size={16}/> Download Original ({f.original_name} · {formatBytes(f.size)})
                  </button>
                ))}
              </div>
            ) : (
              <div className="no-file-client-note">
                <span>Client did not attach a file with this submission.</span>
                <Link className="btn small secondary" to="/admin/create-report">Upload Excel Manually →</Link>
              </div>
            )}
          </div>
        </div>

        {r.requested_areas && r.requested_areas.length > 0 && (
          <div className="client-intent-tags">
            <small>Client Focus Areas:</small>
            {r.requested_areas.map((tag, i) => (
              <span className="intent-tag" key={i}>{tag}</span>
            ))}
          </div>
        )}

        {r.additional_info && (
          <div className="client-instructions-box">
            <b>Client Notes:</b> <span>{r.additional_info}</span>
          </div>
        )}
      </div>

      {message && <div className="success analysis-notice">{message}</div>}

      <div className="kpis">
        <K title="Revenue" value={money(c.revenue)} text="Gross business revenue" icon={TrendingUp}/>
        <K title="Expenses" value={money(c.expenses)} text="Total operating expenses" icon={BarChart3}/>
        <K title="Net Profit" value={money(c.profit)} text="Revenue − expenses" icon={Wallet}/>
        <K title="Profit Margin" value={pct(c.margin)} text="Net operating yield" icon={ArrowUpRight}/>
      </div>

      <div className="analysis-modern-grid">
        <div className="panel">
          <div className="panel-title">
            <div>
              <p className="eyebrow">FINANCIAL DATA INPUT</p>
              <h2>Validated Metrics & Cost Breakdown</h2>
            </div>
            <span className="delivery-badge">Admin Review Mode</span>
          </div>

          <div className="financial-form admin-financial-form">
            <label className="admin-financial-field">
              <span>Gross Revenue (INR)</span>
              <div className="admin-input-wrap">
                <span className="currency">₹</span>
                <input type="number" value={form.revenue} onChange={e => set('revenue', e.target.value)} placeholder="0"/>
              </div>
              <small>Total recognized business revenue</small>
            </label>

            <label className="admin-financial-field">
              <span>Total Operating Expenses (INR)</span>
              <div className="admin-input-wrap">
                <span className="currency">₹</span>
                <input type="number" value={form.expenses} onChange={e => set('expenses', e.target.value)} placeholder="0"/>
              </div>
              <small>Total operational and cost outflows</small>
            </label>

            <label className="admin-financial-field">
              <span>Net Profit (INR)</span>
              <div className="admin-input-wrap">
                <span className="currency">₹</span>
                <input type="number" value={form.profit} onChange={e => set('profit', e.target.value)} placeholder="0"/>
              </div>
              <small>Auto-calculated as Revenue − Expenses</small>
            </label>

            <label className="admin-financial-field">
              <span>Net Margin (%)</span>
              <div className="admin-input-wrap">
                <input type="number" step="0.1" value={form.margin} onChange={e => set('margin', e.target.value)} placeholder="0.0"/>
                <span className="percent">%</span>
              </div>
              <small>Profitability ratio relative to revenue</small>
            </label>

            <label className="admin-financial-field wide">
              <span>Expense Categories & Allocation</span>
              <textarea
                rows="7"
                value={form.categories}
                onChange={e => set('categories', e.target.value)}
                placeholder={'Raw Materials: 2520000\nLabour: 630000\nPower & Utilities: 310000\nTransport: 240000\nMaintenance: 160000\nOther: 350000'}
              />
              <small>Enter one line per category formatted as "Category: Amount"</small>
            </label>

            <label className="admin-financial-field wide">
              <span>Strategic Observations & Key Findings</span>
              <textarea
                rows="6"
                value={form.findings}
                onChange={e => set('findings', e.target.value)}
                placeholder={'Raw materials represent over 60% of cost outflows.\nLabour costs increased due to seasonal overtime.\nTransport expenses should be renegotiated with regional carriers.'}
              />
              <small>Enter one strategic observation per line</small>
            </label>
          </div>
        </div>

        <div className="panel analysis-side-card">
          <p className="eyebrow">WORKFLOW ACTIONS</p>
          <h2>Build FinSight Report</h2>
          <p>Once you validate the numbers above, clicking Save & Build creates the PDF incorporating FinSight corporate layout and case study modeling.</p>

          <div className="side-action-buttons">
            {r.files?.length > 0 && (
              <button
                className="btn secondary full"
                onClick={() => download(`/files/${r.files[0].id}`, r.files[0].original_name)}
              >
                <Download size={16}/> Download Client File ({r.files[0].original_name})
              </button>
            )}

            {r.reports?.length ? (
              <button
                className="btn full"
                onClick={() => download(`/reports/${r.reports[r.reports.length - 1].id}/download`, safeName(r.reports[r.reports.length - 1].title) + '.pdf')}
              >
                <Download size={16}/> Download Latest Created Report
              </button>
            ) : (
              <Link className="btn full" to="/admin/create-report">Upload Excel & Build Report</Link>
            )}

            <Link className="text-action center-text" to="/admin/reports">Open Report Management & Delivery →</Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function CreateReport({requests, refresh}) {
  const [rid, setRid] = useState(localStorage.getItem('finsight_selected_request') || requests[0]?.id || '');
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [a, setA] = useState(null);

  const r = requests.find(x => x.id === rid);

  async function process() {
    if (!rid || !file) return;
    setBusy(true);
    setMsg('');
    try {
      const x = await api.uploadAndAnalyze(rid, file);
      setA(x.analysis);
      await refresh();
      setMsg('Financial file processed successfully. Your editable FinSight executive draft is ready.');
    } catch (e) {
      setMsg(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">REPORT FACTORY</p>
          <h1>Create Client Report</h1>
          <p>Upload Excel/CSV data or inspect the client's submitted original report to generate a complete executive financial analysis.</p>
        </div>
      </div>

      <div className="factory-progress">
        <span className="active"><b>01</b> Source Data</span>
        <span className={a ? 'active' : ''}><b>02</b> Processing</span>
        <span><b>03</b> Review & Edit</span>
        <span><b>04</b> Delivery</span>
      </div>

      <div className="create-grid">
        <div className="panel">
          <p className="eyebrow">CLIENT ENGAGEMENT</p>
          <h2>Select Business</h2>
          <select
            className="big-select"
            value={rid}
            onChange={e => {
              setRid(e.target.value);
              localStorage.setItem('finsight_selected_request', e.target.value);
              setA(null);
            }}
          >
            {requests.map(x => (
              <option value={x.id} key={x.id}>
                {x.business_name} · {x.client_name} ({x.files?.length || 0} client file{x.files?.length === 1 ? '' : 's'})
              </option>
            ))}
          </select>

          {/* Client Original File Bar */}
          {r?.files && r.files.length > 0 && (
            <div className="client-source-badge-bar">
              <div>
                <small className="eyebrow">ORIGINAL REPORT SENT BY CLIENT</small>
                <b>{r.files[0].original_name}</b>
                <span className="text-muted">({formatBytes(r.files[0].size)})</span>
              </div>
              <button
                className="btn small secondary"
                onClick={() => download(`/files/${r.files[0].id}`, r.files[0].original_name)}
                title="Download the original file sent by the client"
              >
                <Download size={13}/> Download Original
              </button>
            </div>
          )}

          <div className="excel-drop">
            <FileSpreadsheet size={42}/>
            <b>{file ? file.name : 'Upload New Excel or CSV Dataset'}</b>
            <span>Excel (.xlsx, .xlsm, .xls) or CSV · Up to 20 MB</span>
            <input type="file" accept=".xlsx,.xlsm,.xls,.csv" onChange={e => setFile(e.target.files?.[0] || null)}/>
            {file && <small className="file-ready-tag">File selected: {file.name} ({formatBytes(file.size)})</small>}
          </div>

          <button className="btn full" disabled={!file || busy} onClick={process}>
            {busy ? (
              <><RefreshCw className="spin"/> Extracting & Generating Report…</>
            ) : (
              <><UploadCloud size={16}/> Upload & Run Extraction</>
            )}
          </button>

          {msg && <div className={msg.includes('successfully') ? 'success' : 'error'}>{msg}</div>}
        </div>

        <div className="panel">
          <p className="eyebrow">ANALYTICAL ENGINE</p>
          <h2>Extracted Financial Components</h2>
          <div className="engine-list">
            <div>
              <CheckCircle2/>
              <span>
                <b>Revenue Recognition</b>
                <small>Aggregates gross revenue, invoiced sales, and detects turnover period.</small>
              </span>
            </div>
            <div>
              <CheckCircle2/>
              <span>
                <b>Operating Cost Breakdown</b>
                <small>Groups raw materials, labour, overhead, logistics, and ranks cost concentration.</small>
              </span>
            </div>
            <div>
              <CheckCircle2/>
              <span>
                <b>Profitability & Net Margin</b>
                <small>Evaluates EBITDA, net operating income, and margin protection ratios.</small>
              </span>
            </div>
            <div>
              <CheckCircle2/>
              <span>
                <b>Case Study Decision Matrix</b>
                <small>Auto-populates senior debt vs equity partner trade-offs and financial sensitivity.</small>
              </span>
            </div>
          </div>

          {a && (
            <div className="processed-summary">
              <span>Processed Financial Health</span>
              <b>{money(a.revenue)}</b>
              <small>Revenue · {pct(a.margin)} Net Margin · {Object.keys(a.expense_categories || {}).length} Cost Dimensions</small>
              <Link className="btn small" to="/admin/reports">Open Report Library →</Link>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function Reports({requests, refresh}) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState('');
  const [detail, setDetail] = useState(null);

  const reports = useMemo(() =>
    requests.flatMap(r =>
      (r.reports || []).map(x => ({
        ...x,
        business: r.business_name,
        client: r.client_name,
        requestId: r.id,
        requestFiles: r.files || [],
        requestStatus: r.status,
        reportStatus: x.status || (!x.sent_at ? 'Ready' : 'Delivered')
      }))
    )
    .filter(x => (`${x.title} ${x.business} ${x.client}`).toLowerCase().includes(query.toLowerCase()))
    .filter(x => filter === 'all' || (filter === 'sent' ? x.sent_at : filter === 'ready' ? x.reportStatus === 'Ready' : true)),
    [requests, query, filter]
  );

  async function open(x) {
    setSelected(x);
    try {
      setDetail(await api.reportDetail(x.id));
    } catch {
      setDetail(null);
    }
  }

  async function send(id) {
    setBusy(id);
    try {
      await api.sendReport(id);
      await refresh();
      if (selected?.id === id) setSelected(null);
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy('');
    }
  }

  async function dl(id, name) {
    try {
      await download(`/reports/${id}/download`, name.replace(/[^a-z0-9]+/gi, '_') + '.pdf');
    } catch (e) {
      alert(e.message);
    }
  }

  async function del(id) {
    if (!confirm('Delete this report? It will also be removed from the client portal.')) return;
    setBusy(id);
    try {
      await api.deleteReport(id);
      setSelected(null);
      setDetail(null);
      await refresh();
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy('');
    }
  }

  return (
    <section className="dash reports-page">
      <div className="dash-head">
        <div>
          <p className="eyebrow">EXECUTIVE REPORT MANAGEMENT</p>
          <h1>Financial Reports</h1>
          <p>Inspect generated advisory reports, download source client data, edit executive wording, and deliver to clients.</p>
        </div>
        <Link className="btn" to="/admin/create-report"><UploadCloud size={16}/> Create Report</Link>
      </div>

      <div className="report-stats">
        <div><span>Total Reports</span><b>{reports.length}</b></div>
        <div><span>Ready for Delivery</span><b>{reports.filter(x => !x.sent_at).length}</b></div>
        <div><span>Delivered to Clients</span><b>{reports.filter(x => x.sent_at).length}</b></div>
        <div><span>Client Businesses</span><b>{new Set(reports.map(x => x.requestId)).size}</b></div>
      </div>

      <div className="report-toolbar panel">
        <input
          placeholder="Search by report title, business name or client email…"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="all">All Reports</option>
          <option value="sent">Delivered Reports</option>
          <option value="ready">Ready Reports</option>
        </select>
      </div>

      <div className="reports-layout">
        <div className="panel report-table-modern responsive-report-table">
          <div className="report-table-head">
            <span>Report Title</span>
            <span>Business / Client</span>
            <span>Created</span>
            <span>Status</span>
            <span>Client Source</span>
            <span>Actions</span>
          </div>

          {reports.length ? reports.map(x => (
            <div className="report-table-row" key={x.id}>
              <span>
                <b>{x.title}</b>
                <small>Ref #{x.id.slice(0, 8).toUpperCase()}</small>
              </span>
              <span>
                <b>{x.business}</b>
                <small>{x.client}</small>
              </span>
              <span>{date(x.created_at)}</span>
              <span className={x.reportStatus === 'Delivered' ? 'delivery-badge' : x.reportStatus === 'Draft' ? 'status draft-status' : 'status'}>
                {x.reportStatus || 'Ready'}
              </span>
              <span>
                {x.requestFiles && x.requestFiles.length > 0 ? (
                  <button
                    className="btn-download-subtle"
                    title={`Download original file sent by client: ${x.requestFiles[0].original_name}`}
                    onClick={() => download(`/files/${x.requestFiles[0].id}`, x.requestFiles[0].original_name)}
                  >
                    <Download size={13}/> Original File
                  </button>
                ) : (
                  <span className="no-file-pill-small">No source</span>
                )}
              </span>
              <span className="row-actions">
                <button title="Preview / Inspect" onClick={() => open(x)}><Eye size={15}/></button>
                <button title="Download PDF" onClick={() => dl(x.id, x.title)}><Download size={15}/></button>
                <button title="Delete Report" className="danger-icon" disabled={busy === x.id} onClick={() => del(x.id)}><Trash2 size={15}/></button>
              </span>
            </div>
          )) : (
            <div className="empty">No reports match your filters.</div>
          )}
        </div>

        <ReportPanel
          report={selected}
          detail={detail}
          busy={busy}
          requests={requests}
          onClose={() => { setSelected(null); setDetail(null); }}
          onSend={send}
          onDownload={dl}
          onDelete={del}
        />
      </div>
    </section>
  );
}

function ReportPanel({report, detail, busy, requests, onClose, onSend, onDownload, onDelete}) {
  const [edit, setEdit] = useState(false);

  const defaultCase = {
    option_a: {
      name: 'Option A: Senior Debt Financing',
      advantages: ['No equity dilution for founders', 'Interest tax shields lower effective financing cost', 'Lower theoretical WACC', 'Higher EPS/ROE upon successful project execution'],
      disadvantages: ['Mandatory interest servicing elevates insolvency risk', 'Debt Service Coverage Ratio (DSCR) compresses', 'Lender covenants constrain operational freedom']
    },
    option_b: {
      name: 'Option B: Strategic Equity / Private Equity Partner',
      advantages: ['Substantially lower leverage (D/E ratio < 0.35x)', 'Resilient interest coverage (>2.5x safety buffer)', 'Institutional governance and expansion expertise', 'Zero debt redemption drain during unexpected market delays'],
      disadvantages: ['Minority equity dilution (~11.6% shareholding)', 'Board seats and tag-along covenants', 'Higher long-term cost of equity']
    },
    final_decision: 'Option B (Strategic Equity Partner)',
    considering: 'Liquidity cushion, sensitivity to project delays, competitive market pressures, cash-flow buffer preservation, and enterprise valuation security.'
  };

  const [form, setForm] = useState({
    title: '',
    executive_summary: '',
    findings: [],
    recommendations: [],
    analyst_notes: '',
    case_study: defaultCase
  });

  useEffect(() => {
    if (detail) {
      setForm({
        title: detail.content?.title || detail.title || '',
        executive_summary: detail.content?.executive_summary || '',
        findings: detail.content?.findings || [],
        recommendations: detail.content?.recommendations || [],
        analyst_notes: detail.content?.analyst_notes || '',
        case_study: detail.content?.case_study || defaultCase
      });
    }
  }, [detail]);

  if (!report) {
    return (
      <div className="panel report-inspector empty-inspector">
        <FileText size={32}/>
        <b>Select a Report to Inspect</b>
        <span>Preview corporate layout, download client original dataset, edit narrative, or deliver to client.</span>
      </div>
    );
  }

  const req = requests.find(r => r.id === report.requestId);

  const updateCase = (side, key, value) => setForm(f => ({
    ...f,
    case_study: {
      ...f.case_study,
      [side]: {
        ...f.case_study[side],
        [key]: value
      }
    }
  }));

  const save = async () => {
    try {
      await api.editReport(report.id, form);
      setEdit(false);
      alert('Report draft updated successfully. Download the PDF to view the newly compiled report.');
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="panel report-inspector enhanced-inspector">
      <div className="inspector-head">
        <div>
          <span className="eyebrow">EXECUTIVE REPORT DOSSIER</span>
          <h2>{report.business}</h2>
          <small>{report.client} · Ref #{report.id.slice(0, 8).toUpperCase()} · Created {date(report.created_at)}</small>
        </div>
        <button className="icon-close" onClick={onClose} title="Close inspector">×</button>
      </div>

      {/* Client Original Report Quick Download in Inspector */}
      {req?.files && req.files.length > 0 && (
        <div className="inspector-original-file-bar">
          <div>
            <small>Client Source File:</small>
            <b>{req.files[0].original_name}</b>
          </div>
          <button
            className="btn small secondary"
            onClick={() => download(`/files/${req.files[0].id}`, req.files[0].original_name)}
            title="Download the original file sent by the client"
          >
            <Download size={13}/> Download Original
          </button>
        </div>
      )}

      {edit ? (
        <div className="inspector-edit-mode">
          <label>
            Report Title
            <input value={form.title} onChange={e => setForm({...form, title: e.target.value})}/>
          </label>

          <label>
            Executive Financial Summary
            <textarea rows="5" value={form.executive_summary} onChange={e => setForm({...form, executive_summary: e.target.value})}/>
          </label>

          <EditableList label="Strategic Findings & Diagnostics" value={form.findings} onChange={v => setForm({...form, findings: v})}/>
          <EditableList label="Actionable Recommendations (Phased Roadmap)" value={form.recommendations} onChange={v => setForm({...form, recommendations: v})}/>

          <div className="case-study-editor">
            <p className="eyebrow">CASE STUDY DECISION MATRIX</p>
            <div className="case-study-columns">
              <div>
                <h3>{form.case_study.option_a?.name || 'Option A'}</h3>
                <EditableList label="Advantages" value={form.case_study.option_a?.advantages || []} onChange={v => updateCase('option_a', 'advantages', v)}/>
                <EditableList label="Disadvantages" value={form.case_study.option_a?.disadvantages || []} onChange={v => updateCase('option_a', 'disadvantages', v)}/>
              </div>
              <div>
                <h3>{form.case_study.option_b?.name || 'Option B'}</h3>
                <EditableList label="Advantages" value={form.case_study.option_b?.advantages || []} onChange={v => updateCase('option_b', 'advantages', v)}/>
                <EditableList label="Disadvantages" value={form.case_study.option_b?.disadvantages || []} onChange={v => updateCase('option_b', 'disadvantages', v)}/>
              </div>
            </div>
            <label>
              Recommended Final Strategic Decision
              <input value={form.case_study.final_decision} onChange={e => setForm({...form, case_study: {...form.case_study, final_decision: e.target.value}})}/>
            </label>
            <label>
              Core Evaluation Rationale (Considering)
              <textarea rows="3" value={form.case_study.considering} onChange={e => setForm({...form, case_study: {...form.case_study, considering: e.target.value}})}/>
            </label>
          </div>

          <label>
            Lead Analyst Notes & Certification
            <textarea rows="3" value={form.analyst_notes} onChange={e => setForm({...form, analyst_notes: e.target.value})}/>
          </label>

          <div className="report-action-stack">
            <button className="btn" onClick={save}><Save size={15}/> Save Report Draft</button>
            <button className="btn secondary" onClick={() => setEdit(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <div className="inspector-view-mode">
          <div className="report-detail-summary">
            <div>
              <span>GROSS REVENUE</span>
              <b>{money(detail?.analysis?.revenue)}</b>
            </div>
            <div>
              <span>TOTAL COSTS</span>
              <b>{money(detail?.analysis?.expenses)}</b>
            </div>
            <div>
              <span>NET PROFIT</span>
              <b>{money(detail?.analysis?.profit)}</b>
            </div>
            <div>
              <span>NET MARGIN</span>
              <b className="positive-text">{pct(detail?.analysis?.margin)}</b>
            </div>
          </div>

          <div className="preview-copy">
            <div className="preview-section-title">
              <span className="eyebrow">EXECUTIVE SUMMARY</span>
            </div>
            <p className="summary-paragraph">{detail?.content?.executive_summary || 'Executive summary generated by FinSight.'}</p>

            <div className="preview-section-title">
              <span className="eyebrow">STRATEGIC OBSERVATIONS & FINDINGS</span>
            </div>
            <div className="findings-pill-stack">
              {(detail?.content?.findings || []).map((x, i) => (
                <div className="finding-pill" key={i}>
                  <CheckCircle2 size={14}/>
                  <span>{x}</span>
                </div>
              ))}
            </div>

            <div className="preview-section-title">
              <span className="eyebrow">ACTIONABLE RECOMMENDATIONS ROADMAP</span>
            </div>
            <div className="recs-pill-stack">
              {(detail?.content?.recommendations || []).map((x, i) => (
                <div className="rec-pill" key={i}>
                  <span className="rec-step">{i + 1}</span>
                  <span>{x}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="case-study-preview">
            <p className="eyebrow">CASE STUDY · STRATEGIC DECISION MATRIX</p>
            <div className="case-study-table">
              <div className="case-head-row">
                <b>Option A (Senior Debt)</b>
                <b>Dimension</b>
                <b>Option B (Equity Partner)</b>
              </div>
              <div className="case-data-row">
                <span>{(detail?.content?.case_study?.option_a?.advantages || defaultCase.option_a.advantages).join(' • ')}</span>
                <b className="dimension-label">Advantages</b>
                <span>{(detail?.content?.case_study?.option_b?.advantages || defaultCase.option_b.advantages).join(' • ')}</span>
              </div>
              <div className="case-data-row">
                <span>{(detail?.content?.case_study?.option_a?.disadvantages || defaultCase.option_a.disadvantages).join(' • ')}</span>
                <b className="dimension-label">Risks</b>
                <span>{(detail?.content?.case_study?.option_b?.disadvantages || defaultCase.option_b.disadvantages).join(' • ')}</span>
              </div>
            </div>

            <div className="decision-banner">
              <b>Recommended Strategic Decision:</b>
              <span>{detail?.content?.case_study?.final_decision || defaultCase.final_decision}</span>
              <small>Considering: {detail?.content?.case_study?.considering || defaultCase.considering}</small>
            </div>
          </div>

          {detail?.content?.analyst_notes && (
            <div className="analyst-notes-preview">
              <small className="eyebrow">ANALYST NOTES</small>
              <p>{detail.content.analyst_notes}</p>
            </div>
          )}

          <div className="report-action-grid">
            <button className="btn" onClick={() => setEdit(true)}><Edit3 size={15}/> Edit Report</button>
            <button className="btn secondary" onClick={() => onDownload(report.id, report.title)}><Download size={15}/> Download PDF</button>
            <button className="btn secondary" onClick={() => openPdf(`/reports/${report.id}/download`)}><Eye size={15}/> View PDF</button>
            {req?.files && req.files.length > 0 && (
              <button
                className="btn secondary"
                title="Download original file sent by client"
                onClick={() => download(`/files/${req.files[0].id}`, req.files[0].original_name)}
              >
                <Download size={15}/> Client Original File
              </button>
            )}
            {!report.sent_at && (
              <button className="btn send-btn" disabled={busy === report.id} onClick={() => onSend(report.id)}>
                <Send size={15}/> {busy === report.id ? 'Sending…' : 'Deliver to Client'}
              </button>
            )}
            <button className="danger-btn" disabled={busy === report.id} onClick={() => onDelete(report.id)}>
              <Trash2 size={15}/> Delete Report
            </button>
          </div>

          <div className="delivery-history">
            <Clock3 size={15}/>
            <span>{report.sent_at ? `Delivered to client on ${date(report.sent_at)}` : 'Status: Ready for client delivery'}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function EditableList({label, value, onChange}) {
  return (
    <label>
      {label}
      <textarea
        rows="6"
        value={value.join('\n')}
        onChange={e => onChange(e.target.value.split('\n').map(x => x.trim()).filter(Boolean))}
        placeholder="One item per line"
      />
    </label>
  );
}

function Clients({clients, requests}) {
  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">CLIENT RELATIONSHIPS</p>
          <h1>Business Portfolio</h1>
          <p>Client identity, company classifications, and engagement history.</p>
        </div>
      </div>
      <div className="panel portfolio-table responsive-portfolio-table">
        <div className="table-head">
          <span>Business Name</span>
          <span>Owner / Contact</span>
          <span>Industry</span>
          <span>Requests</span>
          <span>Account Status</span>
        </div>
        {clients.map(c => (
          <div className="table-row" key={c.id}>
            <span><b>{c.business_name}</b><small>{c.email}</small></span>
            <span>{c.full_name}<small>{c.phone}</small></span>
            <span>{c.business_type}</span>
            <span>{requests.filter(r => r.client_email === c.email).length} engagements</span>
            <span className="delivery-badge">Active Client</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Messages({requests, user}) {
  const [rid, setRid] = useState(requests[0]?.id);
  const [items, setItems] = useState([]);
  const [body, setBody] = useState('');

  useEffect(() => {
    if (rid) api.messages(rid).then(setItems);
  }, [rid]);

  async function send() {
    if (!body.trim()) return;
    const m = await api.sendMessage(rid, body.trim());
    setItems(x => [...x, m]);
    setBody('');
  }

  return (
    <section className="dash">
      <p className="eyebrow">CLIENT COMMUNICATION</p>
      <h1>Client Conversations</h1>
      <p>Discuss financial findings, methodology, and report deliverables with client management.</p>
      <div className="message-layout responsive-message-layout">
        <div className="panel message-threads-panel">
          {requests.map(r => (
            <button
              className={'message-thread ' + (rid === r.id ? 'selected' : '')}
              key={r.id}
              onClick={() => setRid(r.id)}
            >
              <b>{r.business_name}</b>
              <span>{r.client_name}</span>
              <small>{r.status}</small>
            </button>
          ))}
        </div>
        <div className="panel chat">
          <div className="chat-header">
            <b>{requests.find(r => r.id === rid)?.client_name || 'Client'}</b>
            <small>{requests.find(r => r.id === rid)?.business_name}</small>
          </div>
          <div className="chat-list">
            {items.map(m => (
              <div className={m.sender_id === user?.id ? 'bubble mine' : 'bubble'} key={m.id}>
                <b>{m.sender_name}</b>
                <span>{m.body}</span>
                <small>{new Date(m.created_at).toLocaleString()}</small>
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              value={body}
              onChange={e => setBody(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder="Message client…"
            />
            <button className="btn" onClick={send}><Send size={15}/> Send</button>
          </div>
        </div>
      </div>
    </section>
  );
}

function ContactInquiries() {
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState('All');
  const [notice, setNotice] = useState('');

  async function load() {
    try {
      setItems(await api.contactInquiries());
    } catch (e) {
      setNotice(e.message);
    }
  }

  useEffect(() => { load(); }, []);

  async function status(id, value) {
    setBusy(id);
    setNotice('');
    try {
      await api.updateContactStatus(id, value);
      setItems(x => x.map(i => i.id === id ? {...i, status: value} : i));
    } catch (e) {
      setNotice(e.message);
    } finally {
      setBusy(false);
    }
  }

  const visible = filter === 'All' ? items : items.filter(x => x.status === filter);

  return (
    <section className="dash">
      <div className="dash-head">
        <div>
          <p className="eyebrow">PUBLIC INQUIRIES</p>
          <h1>Contact Inquiries</h1>
          <p>Messages received from prospective clients on the FinSight website.</p>
        </div>
        <div className="contact-inquiry-tools">
          <select value={filter} onChange={e => setFilter(e.target.value)}>
            <option>All</option>
            <option>New</option>
            <option>In Progress</option>
            <option>Replied</option>
            <option>Archived</option>
          </select>
          <button className="btn secondary" onClick={load}><RefreshCw size={15}/> Refresh</button>
        </div>
      </div>

      {notice && <div className="error page-message">{notice}</div>}

      <div className="contact-inquiry-list">
        {visible.length === 0 ? (
          <div className="panel empty">No contact inquiries found.</div>
        ) : (
          visible.map(x => (
            <article className="panel contact-inquiry-card" key={x.id}>
              <div className="contact-inquiry-head">
                <div>
                  <span className="status">{x.status}</span>
                  <h2>{x.full_name}</h2>
                  <small>{x.business_name || 'Business not specified'} · {date(x.created_at)}</small>
                </div>
                <select disabled={busy === x.id} value={x.status} onChange={e => status(x.id, e.target.value)}>
                  <option>New</option>
                  <option>In Progress</option>
                  <option>Replied</option>
                  <option>Archived</option>
                </select>
              </div>
              <div className="contact-inquiry-details">
                <a href={`mailto:${x.email}`}>{x.email}</a>
                {x.phone && <a href={`tel:${x.phone}`}>{x.phone}</a>}
              </div>
              <p className="contact-inquiry-message">{x.message}</p>
              <div className="contact-inquiry-actions">
                <a className="btn" href={`mailto:${x.email}?subject=${encodeURIComponent('FinSight Analytics — Consultation Response')}`}>
                  <Send size={15}/> Reply by Email
                </a>
                {x.phone && <a className="btn secondary" href={`tel:${x.phone}`}>Call Client</a>}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function Profile({user}) {
  return (
    <section className="dash">
      <p className="eyebrow">SECURITY & ACCOUNT</p>
      <h1>Admin Profile</h1>
      <div className="panel profile-card">
        <div className="profile-avatar">AD</div>
        <div className="profile-grid">
          <div><small>Name</small><b>{user?.full_name || 'Administrator'}</b></div>
          <div><small>Email</small><b>{user?.email}</b></div>
          <div><small>Username</small><b>{user?.username}</b></div>
          <div><small>Role</small><b>FinSight Corporate Administrator</b></div>
        </div>
      </div>
    </section>
  );
}

function safeName(s) {
  return String(s || 'FinSight_Report').replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '');
}
