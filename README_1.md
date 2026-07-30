# Rushcut Production Ready - Real Working Website

## What you have - production ready, not demo

1. Auth: email/password signup, login, bcryptjs, JWT 30d, logout, middleware.ts protects /dashboard, /billing, /api/rushcut
2. DB: Prisma + Postgres (Neon/Supabase). Models: User, Subscription, Video, Payment
3. Subscription expiry auto-stop: isSubscriptionActive() checks current_period_end. Expired -> canGenerate() returns 403 subscription_expired -> frontend blocks generate, shows renew banner. Owner via OWNER_EMAIL bypasses stealthily (no badge).
4. Payments to YOU: Razorpay INR (₹1499/₹2999/₹5999) -> your Razorpay account, Stripe USD ($19/$39/$79) -> your Stripe account. Webhooks auto-set plan + 30 days.
5. 4K engine: engine/assemble_long.py supports 3840x2160 crf20, 5s to 2.5h, batch concat, brown noise for sleep.
6. All dashboard working end-to-end: login, generate (checks expiry), billing toggle INR/USD, Razorpay/Stripe checkout, videos list from DB, logout.

## Deploy

1. Create Postgres (Neon.tech free):
   DATABASE_URL=postgresql://...

2. Vercel env from .env.example, set OWNER_EMAIL=you@domain.com

3. Deploy:
   npm i
   npx prisma db push
   vercel --prod

4. Engine on Fly.io:
   cd engine && fly launch --name rushcut-engine-4k && fly secrets set ... && fly deploy

5. Webhooks in dashboards:
   Stripe: https://yourdomain.com/api/webhooks/stripe
   Razorpay: https://yourdomain.com/api/webhooks/razorpay

## Test flow

Signup -> Free plan 3 videos 720p 60s max
Pay Razorpay/Stripe -> webhook -> plan pro active 30 days -> can generate 4K 2.5h
Wait 30 days or set current_period_end to past -> isSubscriptionActive false -> generate blocked with renew banner
Owner email -> never blocked, stealth.

## Files added for production
- prisma/schema.prisma, lib/prisma.ts, lib/auth.ts (isSubscriptionActive, canGenerate, isOwner stealth)
- middleware.ts protects routes
- app/login, app/signup, app/dashboard, app/billing, app/page
- app/api/auth/*, api/rushcut, api/pay/*, api/webhooks/*
- engine/* 4K

## Owner stealth
No UI shows owner unlimited. You look like Pro customer. OWNER_EMAIL in env only, never in client bundle. isOwner() check server-only.
