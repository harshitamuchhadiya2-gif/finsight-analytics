import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
export default function BackButton({ fallback }) {
  const navigate = useNavigate();
  const goBack = () => {
    if (window.history.length > 1) navigate(-1); else navigate(fallback || '/');
  };
  return <button type="button" className="back-button" onClick={goBack}><ArrowLeft size={17}/> Back</button>;
}
