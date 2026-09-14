import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Mail, MessageCircle, Phone, Send, CheckCircle2 } from 'lucide-react';
import PublicNav from '../components/PublicNav';
import SiteFooter from '../components/SiteFooter';
import { api } from '../lib/api';

export default function Contact(){
  const [form,setForm]=useState({name:'',email:'',phone:'',message:''});
  const [status,setStatus]=useState('');
  const [busy,setBusy]=useState(false);

  const update=(key,value)=>setForm(prev=>({...prev,[key]:value}));

  async function submit(e){
    e.preventDefault();
    setStatus('');
    if(!form.name.trim()||!form.email.trim()||!form.message.trim()){
      setStatus('Please fill in your name, email and message.');
      return;
    }
    setBusy(true);
    try{
      await api.contact({
        full_name:form.name.trim(),
        business_name:'',
        email:form.email.trim(),
        phone:form.phone.trim(),
        message:form.message.trim()
      });
      setStatus('success');
      setForm({name:'',email:'',phone:'',message:''});
    }catch(err){setStatus(err.message||'Unable to send your message. Please try again.');}
    finally{setBusy(false);}
  }

  return <div className="site contact-page">
    <PublicNav/>
    <main>
      <section className="contact-hero">
        <div className="contact-hero-copy">
          <p className="eyebrow">CONTACT FINSIGHT ANALYTICS</p>
          <h1>Your financial data.<br/><span>Our analysis.</span></h1>
          <p className="contact-lead">WEBSITE IS COMING SOON. DM FOR MORE DETAILS.</p>
          <p className="contact-description">Have questions about financial analysis, cost optimization or how FinSight can help your business? Send us a message and our team will get back to you.</p>
          <div className="contact-tags"><span>FINANCIAL ANALYSIS</span><span>DATA INSIGHTS</span><span>STRATEGIC SOLUTIONS</span></div>
          <h2>For a smarter tomorrow.</h2>
        </div>

        <div className="contact-form-wrap">
          <div className="contact-form-head"><div><p className="eyebrow">GET IN TOUCH</p><h2>Start a conversation</h2></div><MessageCircle size={22}/></div>
          {status==='success' && <div className="success"><CheckCircle2 size={16}/> Thanks! FinSight will contact you shortly.</div>}
          {status && status!=='success' && <div className="error">{status}</div>}
          <form onSubmit={submit}>
            <label>Name<input value={form.name} onChange={e=>update('name',e.target.value)} placeholder="Your name" /></label>
            <label>Email<input type="email" value={form.email} onChange={e=>update('email',e.target.value)} placeholder="you@example.com" /></label>
            <label>Phone <span className="optional">Optional</span><input value={form.phone} onChange={e=>update('phone',e.target.value)} placeholder="Your phone number" /></label>
            <label>Message<textarea value={form.message} onChange={e=>update('message',e.target.value)} placeholder="Tell us how we can help..." /></label>
            <button className="btn full" disabled={busy} type="submit">{busy?'Sending...':'Send Message'} <Send size={16}/></button>
          </form>
        </div>
      </section>

      <section className="contact-info-grid">
        <a className="contact-info-card" href="tel:+917383708602"><Phone/><div><small>CALL US</small><strong>7383708602</strong><span>Discuss your business requirements</span></div></a>
        <a className="contact-info-card" href="mailto:finsightanalytics44@gmail.com"><Mail/><div><small>EMAIL US</small><strong>finsightanalytics44@gmail.com</strong><span>Send your questions or requirements</span></div></a>
        <div className="contact-info-card"><MessageCircle/><div><small>SOCIAL</small><strong>DM FOR MORE DETAILS</strong><span>Connect with FinSight Analytics</span></div></div>
      </section>

      <section className="contact-bottom"><div><p className="eyebrow">READY WHEN YOU ARE</p><h2>Turn numbers into <span>better decisions.</span></h2><p>Understand · Analyze · Improve</p></div><Link className="btn" to="/register">Start With FinSight <ArrowRight size={17}/></Link></section>
    </main>
    <SiteFooter/>
  </div>
}
