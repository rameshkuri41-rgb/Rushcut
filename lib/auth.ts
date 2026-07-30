import bcrypt from "bcryptjs"
import jwt from "jsonwebtoken"
import { prisma } from "./prisma"

export const OWNER_EMAIL = process.env.OWNER_EMAIL || ""
export const JWT_SECRET = process.env.JWT_SECRET || "change_me"

export type Plan = { id:string, limit:number, maxScenes:number, maxMin:number, maxRes:string, priceINR:number, priceUSD:number }
export const PLANS: Record<string, Plan> = {
  free: { id:"free", limit:3, maxScenes:3, maxMin:1, maxRes:"720p", priceINR:0, priceUSD:0 },
  starter: { id:"starter", limit:20, maxScenes:10, maxMin:10, maxRes:"1080p", priceINR:1499, priceUSD:19 },
  pro: { id:"pro", limit:100, maxScenes:150, maxMin:150, maxRes:"4K", priceINR:2999, priceUSD:39 },
  business: { id:"business", limit:300, maxScenes:200, maxMin:150, maxRes:"4K", priceINR:5999, priceUSD:79 },
}

export function isOwner(email:string): boolean { return !!OWNER_EMAIL && email.toLowerCase()===OWNER_EMAIL.toLowerCase() }

export function isSubscriptionActive(user:{email:string, plan:string, status:string, current_period_end:Date|string}){
  if(isOwner(user.email)) return true // stealth owner never expires
  if(user.plan==="free") return true
  if(user.status!=="active") return false
  return new Date(user.current_period_end) > new Date()
}

export async function hashPassword(p:string){ return bcrypt.hash(p,10) }
export async function verifyPassword(p:string,h:string){ return bcrypt.compare(p,h) }

export function signToken(payload:{id:string,email:string}){ return jwt.sign(payload, JWT_SECRET, {expiresIn:"30d"}) }
export function verifyToken(token:string){ try { return jwt.verify(token, JWT_SECRET) as any } catch { return null } }

export async function getUserFromRequest(req:Request){
  const auth = req.headers.get("authorization") || ""
  const token = auth.replace("Bearer ","") || (req as any).cookies?.get?.("token")?.value
  if(!token) return null
  const data = verifyToken(token)
  if(!data) return null
  const user = await prisma.user.findUnique({ where:{email:data.email} })
  return user
}

export function canGenerate(user:any, nScenes:number, durationMin:number, res:string){
  if(!isSubscriptionActive(user)) return { allowed:false, reason:"subscription_expired", message:`Your ${user.plan} plan expired on ${new Date(user.current_period_end).toLocaleDateString()}. Renew to continue.` }
  const plan = PLANS[user.plan] || PLANS.free
  const resOrder:any = {"720p":1,"1080p":2,"4K":3}
  if(user.usage_count >= plan.limit) return { allowed:false, reason:"limit", message:`Monthly limit reached (${plan.limit} videos). Upgrade for more.` }
  if(nScenes > plan.maxScenes) return { allowed:false, reason:"scenes", message:`Max ${plan.maxScenes} scenes for ${plan.id}. Upgrade to Pro for 150 scenes (2.5h).` }
  if(durationMin > plan.maxMin) return { allowed:false, reason:"duration", message:`Max ${plan.maxMin} min for ${plan.id}.` }
  if(resOrder[res] > resOrder[plan.maxRes]) return { allowed:false, reason:"resolution", message:`${res} requires ${plan.maxRes === "720p" ? "Starter (1080p) or Pro (4K)" : "Pro (4K)"} plan.` }
  return { allowed:true }
}
