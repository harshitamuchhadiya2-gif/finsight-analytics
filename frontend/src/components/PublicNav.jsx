import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import Logo from './Logo';

export default function PublicNav(){
  const [open,setOpen]=useState(false);
  const navigate=useNavigate();
  const location=useLocation();

  const close=()=>setOpen(false);
  const goSection=(id)=>{
    close();
    if(location.pathname !== '/') navigate('/');
    setTimeout(()=>document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'}),50);
  };

  return <nav className="public-nav">
    <Link to="/" className="nav-logo" onClick={close}><Logo compact/></Link>

    <div className={`navlinks ${open?'open':''}`}>
      <Link to="/" onClick={close}>Home</Link>
      <button type="button" onClick={()=>goSection('how')}>How We Work</button>
      <button type="button" onClick={()=>goSection('services')}>Services</button>
      <Link to="/about" onClick={close}>About</Link>
      <Link to="/contact" onClick={close}>Contact</Link>
      <div className="mobile-nav-actions">
        <Link to="/login" onClick={close}>Login</Link>
        <Link className="btn" to="/register" onClick={close}>Sign Up</Link>
      </div>
    </div>

    <div className="nav-actions">
      <Link to="/login">Login</Link>
      <Link className="btn" to="/register">Sign Up</Link>
    </div>

    <button className="nav-menu-btn" type="button" aria-label="Toggle navigation" aria-expanded={open} onClick={()=>setOpen(v=>!v)}>
      {open?<X size={23}/>:<Menu size={23}/>} 
    </button>
  </nav>
}
