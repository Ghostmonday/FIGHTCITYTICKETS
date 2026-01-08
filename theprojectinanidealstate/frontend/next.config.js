/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Disable static export for pages that use client-side context
  output: 'standalone',
  // Enable subdomain routing
  async rewrites() {
    return [];
  },
  // Allow all hostnames for subdomain routing
  async headers() {
    return [];
  },
};

module.exports = nextConfig;
