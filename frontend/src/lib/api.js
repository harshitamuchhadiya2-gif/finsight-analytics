const API=(import.meta.env.VITE_API_URL||'').replace(/\/$/,'')+'/api'
export function token(){return localStorage.getItem('finsight_token')}
async function request(path,options={}){
  const headers={...(options.headers||{})}; if(token()) headers.Authorization=`Bearer ${token()}`
  const res=await fetch(API+path,{...options,headers});
  if(!res.ok){let msg='Request failed'; try{const x=await res.json(); const d=x?.detail; msg=typeof d==='string'?d:(Array.isArray(d)?d.map(e=>e?.msg||JSON.stringify(e)).join(', '):(d?JSON.stringify(d):msg))}catch{}; throw new Error(msg)}
  const type=res.headers.get('content-type')||''; return type.includes('application/json')?res.json():res.blob()
}
export const api={
 login:(body)=>request('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 forgotPassword:(body)=>request('/auth/forgot-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 register:(body)=>request('/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 me:()=>request('/me'), requests:()=>request('/requests'),
 createRequest:(body)=>request('/requests',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 upload:(id,files)=>{const fd=new FormData();files.forEach(f=>fd.append('files',f));return request(`/requests/${id}/files`,{method:'POST',body:fd})},
 stats:()=>request('/admin/stats'), clients:()=>request('/admin/clients'), analyze:(id)=>request(`/admin/requests/${id}/analyze`,{method:'POST'}), generateReport:(id)=>request(`/admin/requests/${id}/generate-report`,{method:'POST'}),
 uploadAndAnalyze:(id,file)=>{const fd=new FormData();fd.append('file',file);return request(`/admin/requests/${id}/upload-and-analyze`,{method:'POST',body:fd})},
 reportDetail:(id)=>request(`/admin/reports/${id}`),
 editReport:(id,body)=>request(`/admin/reports/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 deleteReport:(id)=>request(`/admin/reports/${id}`,{method:'DELETE'}),
 status:(id,status)=>request(`/admin/requests/${id}/status`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})}),
 messages:(id)=>request(`/messages/${id}`), sendMessage:(id,body)=>request(`/messages/${id}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({body})}),
 analysis:(id)=>request(`/requests/${id}/analysis`),
 updateFinancials:(id,body)=>request(`/admin/requests/${id}/financials`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 sendReport:(id)=>request(`/admin/reports/${id}/send`,{method:'POST'}),
 contact:(body)=>request('/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),
 contactInquiries:()=>request('/admin/contact-inquiries'),
 updateContactStatus:(id,status)=>request(`/admin/contact-inquiries/${id}/status`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})})
}
export async function openPdf(path){const blob=await request(path);const url=URL.createObjectURL(blob);window.open(url,'_blank','noopener,noreferrer');setTimeout(()=>URL.revokeObjectURL(url),60000)}
export async function download(path,filename){const blob=await request(path);const url=URL.createObjectURL(blob);const a=document.createElement('a');a.style.display='none';a.href=url;a.download=filename;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(url);a.remove()},1000)}
