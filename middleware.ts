import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(req: NextRequest){
  const token = req.cookies.get("token")?.value || req.headers.get("authorization")?.replace("Bearer ","")
  const isAuthRoute = req.nextUrl.pathname.startsWith("/login") || req.nextUrl.pathname.startsWith("/signup") || req.nextUrl.pathname.startsWith("/api/auth")
  const isPublic = req.nextUrl.pathname==="/" || req.nextUrl.pathname.startsWith("/api/webhooks") || isAuthRoute

  if(!isPublic && !token){
    if(req.nextUrl.pathname.startsWith("/api/")) return NextResponse.json({error:"Unauthorized"},{status:401})
    return NextResponse.redirect(new URL("/login", req.url))
  }
  return NextResponse.next()
}
export const config = { matcher: ["/dashboard/:path*", "/api/rushcut/:path*", "/api/pay/:path*", "/billing/:path*", "/videos/:path*"] }
