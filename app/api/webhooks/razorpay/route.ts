import crypto from "crypto"
import { NextRequest } from "next/server"
import { prisma } from "@/lib/prisma"

export async function POST(req: NextRequest){
  const body = await req.text()
  const sig = req.headers.get("x-razorpay-signature")!
  const expected = crypto.createHmac("sha256", process.env.RAZORPAY_KEY_SECRET!).update(body).digest("hex")
  if(sig!==expected) return new Response("Invalid signature",{status:400})
  const event = JSON.parse(body)
  if(event.event==="payment.captured"){
    const p = event.payload.payment.entity
    const email = p.notes?.email
    const planId = p.notes?.planId || "pro"
    if(email){
      const user = await prisma.user.findUnique({where:{email}})
      if(user){
        const end = new Date(Date.now()+30*24*60*60*1000)
        await prisma.user.update({ where:{email}, data:{ plan:planId, status:"active", provider:"razorpay", current_period_start:new Date(), current_period_end:end } })
        await prisma.payment.create({ data:{ user_id:user.id, provider:"razorpay", provider_payment_id:p.id, amount:p.amount, currency:p.currency, plan:planId, status:"captured" } })
        console.log(`[Razorpay] ₹${p.amount/100} for ${email} -> YOUR Razorpay account, plan ${planId} active till ${end}`)
      }
    }
  }
  return Response.json({status:"ok"})
}
