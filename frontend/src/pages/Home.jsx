import {Link} from 'react-router-dom';
import PublicNav from '../components/PublicNav';
import SiteFooter from '../components/SiteFooter';
import {ArrowRight,BarChart3,CheckCircle2,Database,LineChart,ShieldCheck,Target,TrendingUp,WalletCards,Zap} from 'lucide-react';

const services=[
 ['Financial Health Analysis','See revenue, expenses, profit and margin in one clear view.',BarChart3],
 ['Cost & Expense Analysis','Find major cost drivers, unusual spending and savings opportunities.',Target],
 ['Profitability Analysis','Understand what is driving profit and where margins can improve.',TrendingUp],
 ['Revenue Analysis','Track business performance and identify stronger revenue opportunities.',LineChart],
 ['Business Performance','Turn raw business data into practical management insights.',Database],
 ['Custom Analysis','Get a focused review around the questions that matter to your business.',Zap]
];
const process=[['01','Share your business data','Tell us about your business and upload the financial information you want reviewed.'],['02','FinSight analyzes','Our analysis workflow organizes the numbers and highlights important patterns.'],['03','Review clear insights','We turn the findings into simple business language and practical recommendations.'],['04','Receive your report','Your completed report appears in your secure client workspace.']];

export default function Home(){
 return <div className="site landing-v2"><PublicNav/>
  <section className="landing-hero">
   <div className="landing-hero-copy"><div className="hero-kicker"><span className="kicker-dot"/> FINANCIAL ANALYSIS FOR GROWING BUSINESSES</div>
    <h1>Know your numbers.<br/><span>Improve your business.</span></h1>
    <p className="landing-lead">FinSight Analytics helps business owners understand financial performance, control unnecessary costs and make better decisions with confidence.</p>
    <div className="hero-actions"><Link className="btn" to="/register">Start Your Analysis <ArrowRight size={17}/></Link><a className="btn ghost" href="#how">See How It Works</a></div>
    <div className="hero-proof"><span><CheckCircle2 size={15}/> Clear financial insights</span><span><CheckCircle2 size={15}/> Practical recommendations</span><span><CheckCircle2 size={15}/> Secure client workspace</span></div>
   </div>
   <div className="landing-dashboard-visual">
    <div className="visual-glow"/><div className="visual-top"><span>BUSINESS PERFORMANCE</span><b>+18.6%</b></div>
    <div className="visual-kpis"><div><small>Revenue</small><strong>₹12.4L</strong><span>↑ 12.5%</span></div><div><small>Net Profit</small><strong>₹4.9L</strong><span>↑ 8.2%</span></div><div><small>Margin</small><strong>39.5%</strong><span>Healthy</span></div></div>
    <div className="visual-chart"><div className="chart-grid-lines"/><div className="chart-line"><i/><i/><i/><i/><i/><i/><i/></div></div>
    <div className="visual-bottom"><span><ShieldCheck size={14}/> FinSight insight</span><b>Review raw-material costs</b><small>Largest cost driver this period</small></div>
   </div>
  </section>

  <section className="landing-metrics"><div><strong>01</strong><span>Clear analysis workflow</span></div><div><strong>06+</strong><span>Core analysis areas</span></div><div><strong>24/7</strong><span>Secure client access</span></div><div><strong>1</strong><span>Action-focused report</span></div></section>

  <section id="how" className="landing-section process-section"><div className="section-heading"><p className="eyebrow">HOW FINSIGHT WORKS</p><h2>From business data to <span>better decisions.</span></h2><p>Simple for the client. Structured for the analyst. Useful for the business owner.</p></div><div className="process-grid">{process.map(([n,t,d])=><div className="process-card" key={n}><span>{n}</span><div className="process-icon"><ArrowRight size={17}/></div><h3>{t}</h3><p>{d}</p></div>)}</div></section>

  <section id="services" className="landing-section services-section"><div className="section-heading"><p className="eyebrow">WHAT WE ANALYZE</p><h2>Financial clarity across your business.</h2><p>Focus on the numbers that affect profitability, cash flow and sustainable growth.</p></div><div className="landing-service-grid">{services.map(([t,d,I])=><div className="landing-service" key={t}><div className="service-icon"><I size={20}/></div><h3>{t}</h3><p>{d}</p><span>Explore analysis <ArrowRight size={14}/></span></div>)}</div></section>

  <section className="landing-insight"><div className="insight-card"><div><p className="eyebrow">THE FINSIGHT DIFFERENCE</p><h2>Don't just see the numbers.<br/><span>Understand what they mean.</span></h2><p>We present business performance in practical language so you can move from “What happened?” to “What should I do next?”</p><div className="insight-points"><span><CheckCircle2/> Major cost drivers identified</span><span><CheckCircle2/> Profitability opportunities highlighted</span><span><CheckCircle2/> Recommendations explained clearly</span></div></div><div className="insight-score"><small>DECISION CLARITY</small><strong>↑</strong><b>Data → Insight → Action</b><span>Understand · Analyze · Improve</span></div></div></section>

  <section id="about" className="landing-cta"><div><p className="eyebrow">READY TO GET STARTED?</p><h2>Make your financial data<br/><span>work harder for you.</span></h2><p>Start with your business profile and let FinSight turn your data into a clearer view of performance.</p></div><Link className="btn" to="/register">Start With FinSight <ArrowRight size={17}/></Link></section>
  <SiteFooter/>
 </div>
}
