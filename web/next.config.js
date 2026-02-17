/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Exclude recharts from server-side rendering
  experimental: {
    serverComponentsExternalPackages: ['recharts', 'd3-shape', 'd3-scale', 'victory-vendor'],
  },
  webpack: (config, { isServer }) => {
    // Fix for recharts/d3-shape build issue
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      }
    }
    
    // Ignore d3-shape module during build
    config.externals = config.externals || []
    if (isServer) {
      config.externals.push('recharts')
    }
    
    return config
  },
}

module.exports = nextConfig
