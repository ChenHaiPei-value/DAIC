/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['github.com', 'avatars.githubusercontent.com', 'picsum.photos'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    serverActions: true,
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
      {
        source: '/_next/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/github',
        destination: 'https://github.com/daic-org',
        permanent: true,
      },
      {
        source: '/discord',
        destination: 'https://discord.gg/daic',
        permanent: true,
      },
      {
        source: '/twitter',
        destination: 'https://twitter.com/DAIC_org',
        permanent: true,
      },
      {
        source: '/docs',
        destination: '/docs/whitepaper',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;