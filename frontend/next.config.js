/** @type {import('next').NextConfig} */

const isDev = process.env.NODE_ENV === "development";

const nextConfig = {
  assetPrefix: isDev ? undefined : "https://aiarena.net/new-frontend/",

  async rewrites() {
    // In development, we launch the Django app on localhost:8000, and the Next.js app on localhost:3000, which
    // introduces CORS issues. To be able to make requests to the same origin, we proxy our graphql endpoint, so that
    // it's available from localhost:3000.
    if (isDev) {
      return [
        {
          source: "/graphql",
          destination: "http://localhost:8000/graphql/",
        },
      ];
    }

    // We don't need to proxy the API in production, since they're both on the same origin - https://aiarena.net:443.
    // The load balancer is configured to serve either the Django app or the Next.js app based on the path.
    return [];
  },

  env: {
    API_URL: isDev ? "http://localhost:8000" : "https://aiarena.net",
    PUBLIC_PREFIX: isDev ? "." : "/new-frontend",
  },
  trailingSlash: true,
  output: "standalone",
  images: {
    loader: "default",
    path: isDev
      ? "/_next/image"
      : "https://aiarena.net/new-frontend/_next/image",
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "aiarena.net",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "aiarena-mediaproductionbucket-rrwubgechzmq.s3.amazonaws.com",
        pathname: "/**",
      },
    ],
  },
  typescript: {
    ignoreBuildErrors: true,
  },

  compiler: {
    relay: {
      src: "./",
      language: "typescript",
      schema: "./schema.graphql",
    },
  },
};

module.exports = nextConfig;
