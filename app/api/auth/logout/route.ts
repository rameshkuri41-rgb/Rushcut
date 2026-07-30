export async function POST(){
  return new Response(JSON.stringify({ok:true}), { headers: { "Set-Cookie": "token=; Path=/; Max-Age=0" } })
}
