/** @type {import('next').NextConfig} */


const nextConfig = {
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

  // env: {
  //   STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_PUBLISHABLE_STRIPE_KEY,
  //   NEXTAUTH_SECRET: process.env.NEXT_PUBLIC_NEXTAUTH_SECRET,

  //   NEXT_APP_REGION: process.env.NEXT_APP_REGION,

  //   NEXTAUTH_URL_INTERNAL: process.env.NEXT_PUBLIC_SITE_URL,
  //   NEXT_PUBLIC_URL: process.env.NEXT_PUBLIC_SITE_URL,
  //   NEXTAUTH_URL: process.env.NEXT_PUBLIC_SITE_URL,
  // },

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
};

module.exports = nextConfig;
