import { prisma } from "@/lib/prisma"
import { verifyPassword, signToken, isSubscriptionActive } from "@/lib/auth"
import { NextRequest } from "next/server"

export async function POST(req: NextRequest){
  const {email,password} = await req.json()
  const user = await prisma.user.findUnique({where:{email:email.toLowerCase()}})
  if(!user) return Response.json({error:"Invalid email or password"},{status:401})
  const ok = await verifyPassword(password, user.password_hash)
  if(!ok) return Response.json({error:"Invalid email or password"},{status:401})
  const token = signToken({id:user.id,email:user.email})
  return Response.json({ user:{ id:user.id,email:user.email,name:user.name,plan:user.plan,status:user.status,current_period_start:user.current_period_start,current_period_end:user.current_period_end,provider:user.provider,usage_count:user.usage_count, active: isSubscriptionActive(user) }, token })
}
