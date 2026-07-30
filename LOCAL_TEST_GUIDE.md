# LOCAL TEST BEFORE DEPLOY

## Quick steps
1. npm i
2. cp prisma/schema.sqlite.prisma prisma/schema.prisma
3. cp .env.local.example .env.local and set OWNER_EMAIL
4. npx prisma db push
5. Terminal1: cd engine && pip install -r requirements.txt && python server.py
6. Terminal2: npm run dev
7. Open http://localhost:3000 and test signup, free 3 credits block, owner unlimited, expiry auto-stop

See full guide in previous message.
