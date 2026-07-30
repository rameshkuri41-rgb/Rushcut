import "./globals.css"

export const metadata = { title:"Rushcut - Premium 4K Video Engine 5s to 2.5h", description:"Topic in → real 4K .mp4 out. Sleeping history, Razorpay + Stripe." }

export default function RootLayout({children}:{children:React.ReactNode}){
  return (
    <html lang="en">
      <body className="bg-[#050507]">{children}</body>
    </html>
  )
}
