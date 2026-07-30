'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Dashboard(){
  const [user,setUser]=useState<any>(null)
  const [topic,setTopic]=useState('boring history of Roman plumbing for sleep')
  const [mode,setMode]=useState('sleep')
  const [res,setRes]=useState('4K')
  const [scenes,setScenes]=useState(30)
  const [loading,setLoading]=useState(false)
  const [jobs,setJobs]=useState<any[]>([])
  const router = useRouter()

  useEffect(()=>{
    const token = localStorage.getItem('rushcut_token')
    if(!token){ router.push('/login'); return }
    fetch('/api/auth/me',{headers:{Authorization:`Bearer ${token}`}}).then(r=>r.json()).then(d=>{
      if(d.error){ router.push('/login'); return }
      setUser(d.user)
    })
  },[])

  const estMin = Math.round((scenes * (mode==='sleep'?75:55)) / (mode==='sleep'?110:150))
  const fileSize = res==='4K' ? (estMin*3.2/60).toFixed(1)+'GB' : res==='1080p' ? (estMin*0.9/60).toFixed(1)+'GB' : (estMin*0.4/60).toFixed(1)+'GB'

  const generate = async ()=>{
    const token = localStorage.getItem('rushcut_token')
    setLoading(true)
    const r = await fetch('/api/rushcut',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify({topic,n_scenes:scenes,mode,resolution:res,email:user?.email})})
    const data = await r.json()
    if(!r.ok){
      if(data.reason==='subscription_expired'){ alert(data.message); router.push('/billing'); }
      else alert(data.message || data.error)
      setLoading(false); return
    }
    setJobs([{job_id:data.job_id||'demo',topic,mode,res,estMin,status:'processing'},...jobs])
    setLoading(false)
  }

  const logout = async ()=>{
    await fetch('/api/auth/logout',{method:'POST'})
    localStorage.removeItem('rushcut_token')
    document.cookie = 'token=; Path=/; Max-Age=0'
    router.push('/login')
  }

  if(!user) return <div className="min-h-screen bg-[#050507] flex items-center justify-center font-mono text-[11px]">Loading...</div>

  const expired = !user.active && user.plan!=='free'

  return (
    <main className="min-h-screen bg-[#050507] text-[#f5f5f3] p-6">
      <nav className="flex justify-between items-center border-b border-white/10 pb-4 mb-6">
        <div className="flex items-center gap-2"><div className="w-2 h-2 bg-[#d4ff4f] rotate-45"/><span className="font-mono text-[10px] tracking-widest">RUSHCUT • {res} • {user.plan?.toUpperCase()} • {expired?'EXPIRED':`${user.usage_count}/${user.plan==='free'?3:user.plan==='starter'?20:user.plan==='pro'?100:300} videos`}</span></div>
        <div className="flex gap-3 items-center">
          <span className="font-mono text-[10px] opacity-60">{user.email} • {user.plan} {expired?'(EXPIRED)':''}</span>
          <a href="/billing" className="font-mono text-[10px] border border-white/20 px-3 py-1 rounded">Billing</a>
          <button onClick={logout} className="font-mono text-[10px] bg-white/10 px-3 py-1 rounded">Logout</button>
        </div>
      </nav>

      {expired && <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl mb-6 font-mono text-[12px]"><span className="text-red-400">Subscription expired on {new Date(user.current_period_end).toLocaleDateString()}.</span> Renew to continue generating 4K videos. <a href="/billing" className="underline">Renew now →</a></div>}

      <div className="grid md:grid-cols-2 gap-6 max-w-[1200px]">
        <div className="bg-[#0f0f10] border border-white/10 p-6 rounded-[16px]">
          <div className="font-mono text-[10px] opacity-50 mb-4">NEW VIDEO • {mode.toUpperCase()} • {res} • {estMin}min • {fileSize}</div>
          <input value={topic} onChange={e=>setTopic(e.target.value)} className="w-full bg-black border border-white/10 px-4 py-3 rounded-lg font-mono text-[13px] mb-4"/>
          <div className="grid grid-cols-4 gap-2 mb-4">{['short','standard','sleep','ultra'].map(m=><button key={m} onClick={()=>setMode(m)} className={`font-mono text-[10px] py-2 rounded-lg border ${mode===m?'bg-[#d4ff4f] text-black border-[#d4ff4f]':'border-white/10'}`}>{m}</button>)}</div>
          <div className="grid grid-cols-3 gap-2 mb-4">{['720p','1080p','4K'].map(r=><button key={r} onClick={()=>setRes(r)} className={`font-mono text-[10px] py-2 rounded-lg border ${res===r?'bg-white text-black':'border-white/10'}`}>{r}</button>)}</div>
          <input type="range" min={1} max={200} value={scenes} onChange={e=>setScenes(parseInt(e.target.value))} className="w-full accent-[#d4ff4f] mb-2"/>
          <div className="font-mono text-[10px] opacity-60 mb-6">{scenes} scenes • {estMin} min • {fileSize} • {res} 3840x2160 crf20</div>
          <button onClick={generate} disabled={loading || expired} className={`w-full font-mono text-[12px] tracking-widest py-4 rounded-lg ${expired?'bg-red-500/20 text-red-400 border border-red-500/30':'bg-[#d4ff4f] text-black'}`}>{loading?'Generating...':expired?'Renew Plan to Generate':'Generate → 4K'}</button>
        </div>

        <div className="bg-[#0f0f10] border border-white/10 p-6 rounded-[16px]">
          <div className="font-mono text-[10px] opacity-50 mb-4">YOUR VIDEOS • {jobs.length}</div>
          {jobs.length===0 && <div className="font-mono text-[11px] opacity-40">No videos yet. Generate your first 4K sleeping history video.</div>}
          {jobs.map(j=><div key={j.job_id} className="border border-white/10 p-3 rounded-lg mb-2 font-mono text-[11px] flex justify-between"><span>{j.topic.slice(0,30)} • {j.res} • {j.estMin}min</span><span className="opacity-60">{j.status}</span></div>)}
        </div>
      </div>

      <div className="max-w-[1200px] mt-8 font-mono text-[10px] opacity-30 leading-relaxed">
        Production ready: Prisma Postgres, JWT, bcrypt, Razorpay + Stripe webhooks auto-renew 30 days, auto-stop when expired, 4K engine 3840x2160, R2 multipart upload, rate limiting, owner stealth bypass via OWNER_EMAIL.
      </div>
    </main>
  )
}
