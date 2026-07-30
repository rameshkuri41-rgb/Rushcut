import Stripe from "stripe"
import { NextRequest } from "next/server"
import { verifyToken } from "@/lib/auth"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion:"2023-10-16" })

export async function POST(req: NextRequest){
  const auth = req.headers.get("authorization") || ""
  const token = auth.replace("Bearer ","")
  const payload = verifyToken(token)
  if(!payload) return Response.json({error:"Unauthorized"},{status:401})
  const { plan } = await req.json()
  const priceMap:any = { starter: process.env.STRIPE_PRICE_STARTER_USD, pro: process.env.STRIPE_PRICE_PRO_USD, business: process.env.STRIPE_PRICE_BUSINESS_USD }
  const price = priceMap[plan] || priceMap.pro
  const session = await stripe.checkout.sessions.create({
    customer_email: payload.email,
    line_items:[{price,quantity:1}],
    mode:"subscription",
    success_url:`${process.env.NEXT_PUBLIC_SITE_URL}/billing?success=true&provider=stripe`,
    cancel_url:`${process.env.NEXT_PUBLIC_SITE_URL}/billing?canceled=true`,
    metadata:{email:payload.email,plan}
  })
  return Response.json({url:session.url})
}
