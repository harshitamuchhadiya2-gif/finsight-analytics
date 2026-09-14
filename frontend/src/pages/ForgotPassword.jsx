import {useState} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import Logo from '../components/Logo';
import BackButton from '../components/BackButton';
import SiteFooter from '../components/SiteFooter';
import {api} from '../lib/api';
import {Mail,Phone,Lock,Eye,EyeOff,ShieldCheck} from 'lucide-react';

function validPhone(v){return /^(?:\+91[- ]?)?[6-9]\d{9}$/.test(v.trim())}
function Field({icon:Icon,label,type='text',value,onChange,placeholder}){return <label className="modern-auth-field"><span>{label}</span><div><Icon size={17}/><input type={type} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}/></div></label>}

export default function ForgotPassword(){
 const [form,setForm]=useState({email:'',phone:'',password:'',confirm:''}); const [show,setShow]=useState(false); const [busy,setBusy]=useState(false); const [msg,setMsg]=useState(''); const [error,setError]=useState(''); const nav=useNavigate();
 const set=(k,v)=>setForm(x=>({...x,[k]:v}));
 async function submit(e){e.preventDefault();setError('');setMsg('');
  const email=form.email.trim(); const phone=form.phone.trim();
  if(!/^\S+@\S+\.\S+$/.test(email)){setError('Please enter a valid email address.');return}
  if(!validPhone(phone)){setError('Enter a valid Indian phone number, for example 9876543210.');return}
  if(form.password.length<8){setError('New password must be at least 8 characters.');return}
  if(form.password!==form.confirm){setError('Passwords do not match.');return}
  setBusy(true);try{const x=await api.forgotPassword({email,phone,new_password:form.password});setMsg(x.message||'Password updated successfully. You can now sign in.');setTimeout(()=>nav('/login'),1200)}catch(e){setError(e.message)}finally{setBusy(false)}
 }
 return <div className="auth forgot-page"><div className="auth-left"><Logo/><p className="eyebrow">ACCOUNT RECOVERY</p><h1>Get back to your <span>FinSight workspace.</span></h1><p className="lead">Verify the email and phone number linked to your account, then create a new password.</p><div className="recovery-trust"><span><ShieldCheck/> Identity details are checked</span><span><Lock/> Password is stored securely</span></div><p className="tagline">Understand · Analyze · Improve</p></div><div className="auth-right"><div className="auth-back"><BackButton fallback="/login"/></div><div className="auth-card recovery-card"><Logo/><h2>Forgot Password?</h2><p>Enter your registered email and phone number to reset your password.</p><form onSubmit={submit}><Field icon={Mail} label="Registered Email" type="email" value={form.email} onChange={v=>set('email',v)} placeholder="you@example.com"/><Field icon={Phone} label="Registered Phone" value={form.phone} onChange={v=>set('phone',v)} placeholder="9876543210"/><Field icon={Lock} label="New Password" type={show?'text':'password'} value={form.password} onChange={v=>set('password',v)} placeholder="Minimum 8 characters"/><Field icon={Lock} label="Confirm New Password" type={show?'text':'password'} value={form.confirm} onChange={v=>set('confirm',v)} placeholder="Re-enter your password"/><button type="button" className="password-toggle" onClick={()=>setShow(x=>!x)}>{show?<EyeOff size={15}/>:<Eye size={15}/>} {show?'Hide passwords':'Show passwords'}</button>{error&&<div className="error">{error}</div>}{msg&&<div className="success">{msg}</div>}<button className="btn full" disabled={busy}>{busy?'Updating Password…':'Reset Password →'}</button></form><div className="switch"><Link to="/login">← Back to Login</Link></div></div><SiteFooter/></div></div>
}
