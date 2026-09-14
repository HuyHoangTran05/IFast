/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    IFAST_API_BASE_URL: process.env.IFAST_API_BASE_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
