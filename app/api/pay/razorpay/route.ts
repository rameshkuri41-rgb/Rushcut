import { NextRequest } from "next/server"
import Razorpay from "razorpay"
import { verifyToken } from "@/lib/auth"

export async function POST(req: NextRequest){
  const auth = req.headers.get("authorization") || ""
  const token = auth.replace("Bearer ","")
  const payload = verifyToken(token)
  if(!payload) return Response.json({error:"Unauthorized"},{status:401})
  const { planId } = await req.json()
  const amounts:Record<string,number>={starter:149900,pro:299900,business:599900}
  const amount = amounts[planId]||299900
  const razorpay = new Razorpay({ key_id: process.env.RAZORPAY_KEY_ID!, key_secret: process.env.RAZORPAY_KEY_SECRET! })
  const order = await razorpay.orders.create({ amount, currency:"INR", receipt:`rushcut_${planId}_${Date.now()}`, notes:{email:payload.email,planId} })
  return Response.json({ orderId:order.id, amount:order.amount, currency:order.currency, keyId:process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID, planId })
}
