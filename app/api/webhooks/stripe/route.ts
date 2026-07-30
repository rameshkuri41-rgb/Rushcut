import Stripe from "stripe"
import { NextRequest } from "next/server"
import { prisma } from "@/lib/prisma"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion:"2023-10-16" })

export async function POST(req: NextRequest){
  const sig = req.headers.get("stripe-signature")!
  const buf = await req.text()
  let event: Stripe.Event
  try { event = stripe.webhooks.constructEvent(buf, sig, process.env.STRIPE_WEBHOOK_SECRET!) } catch(e:any){ return new Response(`Webhook Error: ${e.message}`,{status:400}) }
  if(event.type==="checkout.session.completed"){
    const session = event.data.object as Stripe.Checkout.Session
    const email = session.customer_email || (session.metadata as any)?.email
    const plan = (session.metadata as any)?.plan || "pro"
    if(email){
      const user = await prisma.user.findUnique({where:{email}})
      if(user){
        const end = new Date(Date.now()+30*24*60*60*1000)
        await prisma.user.update({ where:{email}, data:{ plan, status:"active", provider:"stripe", current_period_start:new Date(), current_period_end:end, stripe_customer_id: session.customer as string } })
        await prisma.payment.create({ data:{ user_id:user.id, provider:"stripe", provider_payment_id: session.id, amount: session.amount_total||0, currency: session.currency||"usd", plan, status:"captured" } })
        console.log(`[Stripe] ${email} paid $${(session.amount_total||0)/100} -> YOUR Stripe account, plan ${plan} active till ${end}`)
      }
    }
  }
  return Response.json({received:true})
}
