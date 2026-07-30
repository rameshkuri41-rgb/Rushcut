# OWNER UNLIMITED GUIDE - How you use unlimited

## 1. Set OWNER_EMAIL in Vercel + Fly.io env (STEALTH, never in client)

Vercel Dashboard -> your project -> Settings -> Environment Variables:
OWNER_EMAIL=you@yourdomain.com  <- your Gmail you login with
JWT_SECRET=random_64_chars
...

Fly.io:
fly secrets set OWNER_EMAIL=you@yourdomain.com --app rushcut-engine-4k

## 2. Login with that exact email

Signup/Login with you@yourdomain.com (must match OWNER_EMAIL exactly, case-insensitive)

You will LOOK LIKE Pro customer (no badge) but backend:
- isOwner(email) returns true
- isSubscriptionActive() always true
- canGenerate() returns allowed:true with reason owner_bypass_unlimited
- Never expires, never blocks, unlimited 4K 2.5h

Check logs:
Vercel logs will show: [OWNER UNLIMITED] you@yourdomain.com generating...

## 3. How to verify owner is working

Login with you@yourdomain.com -> open browser console -> localStorage.getItem('rushcut_token') -> copy -> jwt.io decode -> email should match OWNER_EMAIL

Or call /api/auth/me with token -> response has is_owner: true (only in API, not UI)

If you see free_credits_exhausted as owner, OWNER_EMAIL mismatch! Check env.

## 4. Free Gmail one-time logic

- Each Gmail gets 3 free videos only (free plan limit=3)
- After 3, canGenerate returns free_credits_exhausted -> frontend shows "Free credits exhausted (3/3). Gmail one-time only. Upgrade to Starter ₹1499/$19"
- Signup with same Gmail again -> blocked: "Account already exists with this Gmail. Free is one-time only"
- Paid plans monthly reset (usage_count reset via cron or manual)

## 5. Video not generating fix

Common reasons:

A) Engine not running:
   fly status --app rushcut-engine-4k
   fly logs --app rushcut-engine-4k
   Fix: fly deploy or cd engine && uvicorn server:app --port 8000

B) ENGINE_URL not set in Vercel:
   Vercel env ENGINE_URL=https://your-engine.fly.dev (not localhost)
   NEXT_PUBLIC_ENGINE_URL same

C) R2 not configured:
   S3_BUCKET, S3_ENDPOINT, AWS_... must be set in Fly.io secrets

D) Owner bypass not active but free exhausted:
   You are logged in with non-owner email that used 3 free. Login with OWNER_EMAIL.

Test owner unlimited:
   Login with OWNER_EMAIL -> dashboard shows Pro but usage 100/100 -> try generate 150 scenes 4K 2.5h -> should still work (bypass). If blocked, OWNER_EMAIL env mismatch.

## 6. Production checklist

- OWNER_EMAIL set in both Vercel and Fly.io same value
- DATABASE_URL set, prisma db push done
- ENGINE_URL set correctly
- R2 bucket created, public base set
- Razorpay/Stripe webhooks set
- Test: signup with test@gmail.com -> 3 videos free -> 4th blocked -> pay -> becomes Pro -> can generate 4K
- Test owner: login with OWNER_EMAIL -> generate 200 scenes 4K -> should work even if usage >100