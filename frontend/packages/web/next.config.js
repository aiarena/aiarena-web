/** @type {import('next').NextConfig} */


const nextConfig = {
  async rewrites() {
    // In development, we launch the Django app on localhost:8000, and the Next.js app on localhost:3000, which
    // introduces CORS issues. To be able to make requests to the same origin, we proxy our graphql endpoint, so that
    // it's available from localhost:3000.
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/graphql',
          destination: 'http://localhost:8000/graphql/',
        },
      ];
    }

    // We don't need to proxy the API in production, since they're both on the same origin - https://aiarena.net:443.
    // The load balancer is configured to serve either the Django app or the Next.js app based on the path.
    return [];
  },
  // webpack: (config, { isServer }) => {
  //   config.cache = false;
  //   return config;
  // },
  // reactStrictMode: true,

  // images: {
  //   domains: [
  //     process.env.NEXT_PUBLIC_BUCKET +
  //       ".s3." +
  //       process.env.NEXT_PUBLIC_REGION +
  //       ".amazonaws.com",
  //   ],
  // },

  env: {
    // STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_PUBLISHABLE_STRIPE_KEY,
    // NEXTAUTH_SECRET: process.env.NEXT_PUBLIC_NEXTAUTH_SECRET,
    //
    // NEXT_APP_REGION: process.env.NEXT_APP_REGION,
    //
    // NEXTAUTH_URL_INTERNAL: process.env.NEXT_PUBLIC_SITE_URL,
    // NEXT_PUBLIC_URL: process.env.NEXT_PUBLIC_SITE_URL,
    // NEXTAUTH_URL: process.env.NEXT_PUBLIC_SITE_URL,
    API_URL: process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'https://aiarena.net',
  },

  //Silencing the AWS error inside auth
  // webpack: (config, { isServer }) => {
  //   if (!isServer) {
  //     config.resolve = {
  //       ...config.resolve,
  //       fallback: {
  //         ...config.resolve.fallback,
  //         fs: false,
  //       },
  //     };
  //   }

  //   config.module = {
  //     ...config.module,
  //     exprContextCritical: false,
  //   };
  //   return config;
  // },
  compiler: {
    relay: {
      src: './',
      language: 'typescript',
      schema: './schema.graphql',
    }
  }
};

module.exports = nextConfig;
