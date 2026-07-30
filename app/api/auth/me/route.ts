import { prisma } from "@/lib/prisma"
import { verifyToken, isSubscriptionActive } from "@/lib/auth"
import { NextRequest } from "next/server"

export async function GET(req: NextRequest){
  const auth = req.headers.get("authorization") || req.headers.get("cookie") || ""
  const tokenMatch = auth.match(/token=([^;]+)/)
  const token = auth.startsWith("Bearer ") ? auth.replace("Bearer ","") : tokenMatch ? tokenMatch[1] : ""
  if(!token) return Response.json({error:"Unauthorized"},{status:401})
  const payload = verifyToken(token)
  if(!payload) return Response.json({error:"Invalid token"},{status:401})
  const user = await prisma.user.findUnique({where:{email:payload.email}})
  if(!user) return Response.json({error:"Not found"},{status:404})
  return Response.json({ user:{...user, active: isSubscriptionActive(user)}, active: isSubscriptionActive(user) })
}
