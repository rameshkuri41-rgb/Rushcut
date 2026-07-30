/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: { serverComponentsExternalPackages: ["@prisma/client"] },
  images: { domains: ["pub-*.r2.dev"] }
}
module.exports = nextConfig
