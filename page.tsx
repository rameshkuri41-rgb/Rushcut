export default function Home(){
  return (
    <main className="min-h-screen bg-[#050507] text-[#f5f5f3] p-8">
      <nav className="flex justify-between items-center border-b border-white/10 pb-6 mb-12 max-w-[1200px]">
        <div className="flex items-center gap-2"><div className="w-2 h-2 bg-[#d4ff4f] rotate-45"/><span className="font-mono text-[10px] tracking-[0.2em]">RUSHCUT • PREMIUM 4K • PRODUCTION READY</span></div>
        <div className="flex gap-3"><a href="/login" className="font-mono text-[11px] border border-white/20 px-4 py-2 rounded-lg">Login</a><a href="/signup" className="font-mono text-[11px] bg-[#d4ff4f] text-black px-4 py-2 rounded-lg">Get Started →</a></div>
      </nav>
      <div className="max-w-[1200px]">
        <h1 className="font-display text-[72px] leading-[0.9]">Topic in <span className="text-[#d4ff4f]">→</span> real <span className="text-[#8b5cf6]">4K .mp4</span> out.</h1>
        <p className="font-mono text-[13px] opacity-60 mt-4 max-w-[600px]">Production ready: Auth email/password, JWT, Prisma Postgres, Razorpay INR + Stripe USD → your accounts, auto-stop when subscription expired, 5s to 2.5h, 720p to 4K, sleeping history.</p>
        <div className="grid md:grid-cols-3 gap-4 mt-10">
          <div className="bg-[#0f0f10] border border-white/10 p-6 rounded-[16px]"><div className="font-mono text-[10px] opacity-50">AUTH</div><div className="font-mono text-[11px] mt-2 leading-relaxed">Email/password signup, login, bcrypt, JWT, logout, /login /signup /dashboard /billing protected by middleware.ts. Owner stealth via OWNER_EMAIL.</div></div>
          <div className="bg-[#0f0f10] border border-white/10 p-6 rounded-[16px]"><div className="font-mono text-[10px] opacity-50">SUBSCRIPTION AUTO-STOP</div><div className="font-mono text-[11px] mt-2 leading-relaxed">isSubscriptionActive() checks current_period_end. Expired → canGenerate() returns subscription_expired → 403 → frontend blocks generate, shows renew banner. Webhooks set +30 days.</div></div>
          <div className="bg-[#0f0f10] border border-white/10 p-6 rounded-[16px]"><div className="font-mono text-[10px] opacity-50">PAYMENTS TO YOU</div><div className="font-mono text-[11px] mt-2 leading-relaxed">Razorpay rzp_live_... money → your Razorpay Dashboard. Stripe sk_live_... → your Stripe Balance. Webhooks at /api/webhooks/*</div></div>
        </div>
        <div className="mt-10 flex gap-3"><a href="/signup" className="bg-[#d4ff4f] text-black font-mono text-[12px] px-6 py-3 rounded-lg">Start Free →</a><a href="/login" className="border border-white/20 font-mono text-[12px] px-6 py-3 rounded-lg">Login</a></div>
      </div>
    </main>
  )
}
