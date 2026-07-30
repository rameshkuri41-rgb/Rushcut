import { NextRequest } from "next/server"
import { prisma } from "@/lib/prisma"
import { verifyToken, canGenerate, isSubscriptionActive } from "@/lib/auth"

export async function POST(req: NextRequest){
  const auth = req.headers.get("authorization") || ""
  const token = auth.replace("Bearer ","")
  const payload = verifyToken(token)
  if(!payload) return Response.json({error:"Unauthorized - login required"},{status:401})
  const user = await prisma.user.findUnique({where:{email:payload.email}})
  if(!user) return Response.json({error:"User not found"},{status:404})

  const { topic, n_scenes, mode, resolution } = await req.json()
  const estMin = (n_scenes * (mode==='sleep'?75:55)) / (mode==='sleep'?110:150)

  // AUTO-STOP CHECK
  const check = canGenerate(user, n_scenes, estMin, resolution||"720p")
  if(!check.allowed){
    return Response.json({ error: check.reason, message: (check as any).message, expired: (check as any).reason==="subscription_expired", user: { plan:user.plan, status:user.status, current_period_end:user.current_period_end, active: isSubscriptionActive(user) } }, {status:403})
  }

  const engine = process.env.ENGINE_URL || "http://localhost:8000"
  try {
    const r = await fetch(`${engine}/jobs`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic,n_scenes,mode,resolution})})
    const data = await r.json()
    await prisma.user.update({ where:{id:user.id}, data:{ usage_count: {increment:1} } })
    await prisma.video.create({ data:{ user_id:user.id, job_id:data.job_id, topic, mode, n_scenes, resolution:resolution||"720p", duration_sec: estMin*60, status:"processing" } })
    return Response.json(data)
  } catch(e:any){
    return Response.json({ job_id:"demo_"+Date.now(), status:"processing", message:"Engine offline - demo mode", topic })
  }
}
