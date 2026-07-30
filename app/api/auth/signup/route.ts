import { prisma } from "@/lib/prisma"
import { hashPassword, signToken, isOwner } from "@/lib/auth"
import { NextRequest } from "next/server"

export async function POST(req: NextRequest){
  const {email,password,name} = await req.json()
  if(!email || !password || password.length<6) return Response.json({error:"Email and password min 6 chars required"},{status:400})
  const existing = await prisma.user.findUnique({where:{email:email.toLowerCase()}})
  if(existing) return Response.json({error:"User already exists"},{status:400})
  const hash = await hashPassword(password)
  const user = await prisma.user.create({ data:{ email:email.toLowerCase(), name:name||email.split('@')[0], password_hash:hash, plan:"free", status:"active", is_owner:isOwner(email) } })
  const token = signToken({id:user.id,email:user.email})
  return Response.json({ user:{id:user.id,email:user.email,name:user.name,plan:user.plan,status:user.status,current_period_end:user.current_period_end,is_owner:user.is_owner}, token })
}
