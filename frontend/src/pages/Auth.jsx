import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import BackButton from '../components/BackButton';
import SiteFooter from '../components/SiteFooter';
import { api } from '../lib/api';
import { Mail, Lock, UserRound, Building2, Phone, Eye, EyeOff } from 'lucide-react';

export default function Auth({ register = false }) {
  const [form, setForm] = useState({});
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const nav = useNavigate();

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  async function submit(e) {
    e.preventDefault();
    setError('');
    try {
      if (register && form.password !== form.confirm_password) {
        throw new Error('Passwords do not match');
      }
      const payload = register
        ? form
        : { login: form.login, password: form.password };
      const x = register ? await api.register(payload) : await api.login(payload);
      localStorage.setItem('finsight_token', x.token);
      localStorage.setItem('finsight_user', JSON.stringify(x.user));
      nav(x.user.role === 'admin' ? '/admin' : '/client');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth">
      <div className="auth-left">
        <Logo />
        <p className="eyebrow">{register ? 'JOIN FINSIGHT ANALYTICS' : 'WELCOME BACK'}</p>
        <h1>
          {register ? 'Create Your Account' : 'Turn Your Financial Data Into'}{' '}
          <span>{register ? 'Start Your Journey Towards Better Decisions.' : 'Better Decisions.'}</span>
        </h1>
        <p className="lead">
          {register
            ? 'Get access to professional financial analysis, business insights and personalized reports to help your business grow.'
            : 'Sign in to your FinSight account and continue managing your business analysis.'}
        </p>
        <div className="auth-visual">
          <div className="mini-bars">
            {[25, 38, 32, 52, 64, 70, 86].map((x, i) => (
              <i key={i} style={{ height: `${x}%` }} />
            ))}
          </div>
          <div className="glow-line">╭────╮╭──────╮╭─────╮</div>
        </div>
        <p className="tagline">Understand · Analyze · Improve</p>
      </div>

      <div className="auth-right">
        <div className="auth-back"><BackButton fallback="/" /></div>
        <div className="auth-card">
          <Logo />
          <h2>{register ? 'Register Now' : 'Welcome Back'}</h2>
          <p>{register ? 'Create your account and get started with FinSight.' : 'Sign in to your FinSight account.'}</p>

          <form onSubmit={submit}>
            {register && (
              <>
                <Field I={UserRound} label="Full Name" onChange={(v) => set('full_name', v)} required />
                <Field I={UserRound} label="Username" onChange={(v) => set('username', v)} required />
                <Field I={Building2} label="Business Name" onChange={(v) => set('business_name', v)} required />
                <div className="two">
                  <Field I={Mail} label="Email Address" type="email" onChange={(v) => set('email', v)} required />
                  <Field I={Phone} label="Phone Number" onChange={(v) => set('phone', v)} required />
                </div>
                <select value={form.business_type || ''} onChange={(e) => set('business_type', e.target.value)} required>
                  <option value="">Select business type</option>
                  <option>Retail</option>
                  <option>Restaurant</option>
                  <option>E-commerce</option>
                  <option>Services</option>
                  <option>Manufacturing</option>
                </select>
              </>
            )}

            {!register && (
              <Field I={UserRound} label="Email or Username" onChange={(v) => set('login', v)} required />
            )}

            <Field
              I={Lock}
              label="Password"
              type={show ? 'text' : 'password'}
              onChange={(v) => set('password', v)}
              required
              end={
                <button type="button" className="iconbtn" onClick={() => setShow((v) => !v)}>
                  {show ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              }
            />

            {register && (
              <Field
                I={Lock}
                label="Confirm Password"
                type="password"
                onChange={(v) => set('confirm_password', v)}
                required
              />
            )}

            {error && <div className="error">{error}</div>}
            {!register && <div className="forgot-link"><Link to="/forgot-password">Forgot password?</Link></div>}

            {register && (
              <label className="check">
                <input type="checkbox" required /> I agree to the Terms &amp; Conditions and Privacy Policy
              </label>
            )}

            <button className="btn full" type="submit">
              {register ? 'Create Account →' : 'Sign In →'}
            </button>
          </form>

          <div className="switch">
            {register ? 'Already have an account?' : 'Don’t have an account?'}{' '}
            <Link to={register ? '/login' : '/register'}>{register ? 'Login' : 'Create Account'}</Link>
          </div>
        </div>

        <SiteFooter />
      </div>
    </div>
  );
}

function Field({ I, label, type = 'text', onChange, end, required }) {
  return (
    <label className="field">
      <span>{label}{required ? ' *' : ''}</span>
      <div>
        <I size={17} />
        <input
          type={type}
          placeholder={`Enter ${label.toLowerCase()}`}
          onChange={(e) => onChange(e.target.value)}
          required={required}
        />
        {end}
      </div>
    </label>
  );
}
