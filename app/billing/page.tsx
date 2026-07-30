'use client'
import { useEffect, useState } from 'react'

export default function Billing(){
  const [user,setUser]=useState<any>(null)
  const [currency,setCurrency]=useState<'INR'|'USD'>('INR')
  const [plan,setPlan]=useState('pro')
  useEffect(()=>{
    const token = localStorage.getItem('rushcut_token')
    fetch('/api/auth/me',{headers:{Authorization:`Bearer ${token}`}}).then(r=>r.json()).then(d=>setUser(d.user))
  },[])
  const payRazorpay = async ()=>{
    const token = localStorage.getItem('rushcut_token')
    const r = await fetch('/api/pay/razorpay',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify({planId:plan,email:user?.email})})
    const data = await r.json()
    // @ts-ignore
    const options = { key: data.keyId, amount: data.amount, currency: data.currency, name: 'Rushcut '+plan, order_id: data.orderId, handler: function(){ alert('Payment successful! Subscription active 30 days. Money -> your Razorpay account.'); window.location.reload() }, theme:{color:'#d4ff4f'} }
    // @ts-ignore
    const rzp = new window.Razorpay(options); rzp.open()
  }
  const payStripe = async ()=>{
    const token = localStorage.getItem('rushcut_token')
    const r = await fetch('/api/pay/stripe',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify({plan, email:user?.email})})
    const {url} = await r.json(); window.location.href=url
  }
  if(!user) return <div className="min-h-screen bg-[#050507] flex items-center justify-center font-mono text-[11px]">Loading billing...</div>
  const daysLeft = Math.max(0, Math.ceil((new Date(user.current_period_end).getTime() - Date.now())/86400000))
  const expired = !user.active && user.plan!=='free'
  return (
    <main className="min-h-screen bg-[#050507] text-[#f5f5f3] p-8">
      <h1 className="font-display text-[32px] mb-2">Billing</h1>
      <div className={`p-4 rounded-xl mb-6 font-mono text-[12px] border ${expired?'bg-red-500/10 border-red-500/20 text-red-400':'bg-green-500/10 border-green-500/20'}`}>
        Plan: {user.plan} • Status: {user.status} {expired?'(EXPIRED)':`(Active)`} • Period: {new Date(user.current_period_start).toLocaleDateString()} - {new Date(user.current_period_end).toLocaleDateString()} • {expired?'Expired':`${daysLeft} days left`} • Usage: {user.usage_count} videos • {expired?'Renew to continue':''}
      </div>
      <div className="flex gap-2 mb-6"><button onClick={()=>setCurrency('INR')} className={`font-mono text-[11px] px-4 py-2 rounded border ${currency==='INR'?'bg-white text-black':'border-white/20'}`}>INR ₹</button><button onClick={()=>setCurrency('USD')} className={`font-mono text-[11px] px-4 py-2 rounded border ${currency==='USD'?'bg-white text-black':'border-white/20'}`}>USD $</button></div>
      <div className="grid grid-cols-3 gap-4 max-w-[900px]">
        {[
          {id:'starter', inr:1499, usd:19, feat:'20 vids • 1080p • 10min'},
          {id:'pro', inr:2999, usd:39, feat:'100 vids • 4K • 2.5h • sleep'},
          {id:'business', inr:5999, usd:79, feat:'300 vids • 4K • API • 5 seats'},
        ].map(p=><div key={p.id} onClick={()=>setPlan(p.id)} className={`border p-6 rounded-xl cursor-pointer ${plan===p.id?'border-[#d4ff4f] bg-[#d4ff4f]/5':'border-white/10'}`}><div className="font-mono text-[12px] font-bold">{p.id}</div><div className="font-display text-[28px] mt-2">{currency==='INR'?'₹'+p.inr:'$'+p.usd}<span className="font-mono text-[10px] opacity-50">/mo</span></div><div className="font-mono text-[10px] opacity-60 mt-2">{p.feat}</div></div>)}
      </div>
      <div className="grid grid-cols-2 gap-3 max-w-[900px] mt-6">
        <button onClick={payRazorpay} className="bg-[#5a2fc2] text-white font-mono text-[12px] py-3 rounded-lg">Pay Razorpay {currency==='INR'?'₹'+{starter:1499,pro:2999,business:5999}[plan as any]:'$'+{starter:19,pro:39,business:79}[plan as any]} → Your Account</button>
        <button onClick={payStripe} className="bg-white text-black font-mono text-[12px] py-3 rounded-lg">Pay Stripe ${{starter:19,pro:39,business:79}[plan as any]} → Your Account</button>
      </div>
      <div className="font-mono text-[10px] opacity-40 mt-6 max-w-[900px]">Razorpay money → your Razorpay Dashboard → Settlements. Stripe money → your Stripe Dashboard → Balance. Webhooks auto-set current_period_end = now + 30 days. When expired, canGenerate() returns false and blocks generation automatically. Owner (OWNER_EMAIL) bypasses expiry stealthily.</div>
    </main>
  )
}
