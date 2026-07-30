'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Signup(){
  const [name,setName]=useState(''),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[err,setErr]=useState(''),[loading,setLoading]=useState(false)
  const router = useRouter()
  const submit = async (e:any)=>{
    e.preventDefault(); setLoading(true); setErr('')
    const r = await fetch('/api/auth/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password,name})})
    const data = await r.json()
    if(!r.ok){ setErr(data.error); setLoading(false); return }
    localStorage.setItem('rushcut_token', data.token)
    document.cookie = `token=${data.token}; path=/; max-age=2592000`
    router.push('/dashboard')
  }
  return (
    <main className="min-h-screen bg-[#050507] flex items-center justify-center p-8">
      <div className="w-full max-w-[400px] bg-[#0f0f10] border border-white/10 rounded-[16px] p-8">
        <div className="font-mono text-[10px] tracking-widest opacity-50 mb-6">RUSHCUT • PREMIUM 4K • 3 FREE VIDEOS</div>
        <h1 className="font-display text-[32px] mb-2">Create account</h1>
        <p className="font-mono text-[11px] opacity-60 mb-6">Generate 4K videos 5s to 2.5h, Razorpay + Stripe</p>
        <form onSubmit={submit} className="space-y-4">
          <input value={name} onChange={e=>setName(e.target.value)} placeholder="Name" className="w-full bg-black border border-white/10 px-4 py-3 rounded-lg font-mono text-[13px]"/>
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@domain.com" className="w-full bg-black border border-white/10 px-4 py-3 rounded-lg font-mono text-[13px]"/>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password (min 6 chars)" className="w-full bg-black border border-white/10 px-4 py-3 rounded-lg font-mono text-[13px]"/>
          {err && <div className="font-mono text-[11px] text-red-400 bg-red-500/10 p-3 rounded">{err}</div>}
          <button disabled={loading} className="w-full bg-[#d4ff4f] text-black font-mono text-[12px] tracking-widest py-3 rounded-lg">{loading?'Creating...':'Create account →'}</button>
        </form>
        <div className="font-mono text-[11px] opacity-60 mt-6 text-center">Have account? <a href="/login" className="text-[#d4ff4f]">Login</a></div>
      </div>
    </main>
  )
}
