// "use client";
// import {LoginProvider} from "@/_components/providers/LoginProvider";
// import "./globals.css";
// import {Inter} from "next/font/google";
// import {Quicksand} from "next/font/google";
// import {Gugi} from "next/font/google";
// import RelayEnvironment from "@/_lib/RelayEnvironment";
// import {RelayEnvironmentProvider} from "react-relay";
// import {UserProvider} from "@/_components/providers/UserProvider";
// import { quicksand, gugi } from "@/_styles/fonts"; // Adjust the path as necessary
// import Head from "next/head";
// import { getPublicPrefix } from "@/_lib/getPublicPrefix";

// const inter = Inter({subsets: ["latin"]});
// export const metadata = {
//     title: 'My Application',
//     description: 'Welcome to my application!',
//     icons: {
//       icon: '/icons/favicon.ico', // Default favicon
//       shortcut: '/icons/favicon.ico', // Browser shortcut icon
//       apple: '/icons/favicon-apple-touch-icon.png', // Apple touch icon
//       other: [
//         {
//           rel: 'icon',
//           sizes: '16x16',
//           url: '/icons/favicon-16x16.png',
//         },
//         {
//           rel: 'icon',
//           sizes: '32x32',
//           url: '/icons/favicon-32x32.png',
//         },
//       ],
//     },
//   };

// function RootLayout({children}: { children: React.ReactNode }) {
//     const faviconUrl = `${getPublicPrefix}/assets_logo/img/favicon.ico`;

//     return (
//         <html lang="en">
//         <Head>
//             <link rel="icon" href={faviconUrl} sizes="any"/>
//         </Head>
//         <body
//           className={`${quicksand.variable} ${gugi.variable} font-sans text-center  bg-background-texture`}
//         //   style={{ backgroundImage: `url('${process.env.PUBLIC_PREFIX}/backgrounds/background.gif')` }}
//         >
//         <RelayEnvironmentProvider environment={RelayEnvironment}>
//             <LoginProvider>
//                 <UserProvider>
//                     {children}
//                 </UserProvider>
//             </LoginProvider>
//         </RelayEnvironmentProvider>
//         </body>
//         </html>
//     );
// }

// export default RootLayout;

import "./globals.css";
import { Inter } from "next/font/google";
import { quicksand, gugi } from "@/_styles/fonts"; // Adjust the path as necessary
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import ClientWrapper from "@/_components/providers/ClientWrapper";
import BackgroundTexture from "@/_components/_display/BackgroundTexture";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "AI Arena",
  description: "The Arena for AI!",
  icons: {
    icon: "/favicon.ico", // Default favicon
    shortcut: "/favicon.ico", // Browser shortcut icon
    apple: `${getPublicPrefix()}/assets_logo/img/ai-arena-logo.png`, // Apple touch icon
    other: [
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        url: `${getPublicPrefix()}/assets_logo/img/ai-arena-logo.png`,
      },
      {
        rel: "icon",
        type: "image/svg+xml",
        url: `${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`,
      },
      {
        rel: "icon",
        media: "(prefers-color-scheme: dark)",
        url: `${getPublicPrefix()}/assets_logo/ai_arena_logo_icon_03_4BF_icon.ico`,
      },
      {
        rel: "icon",
        media: "(prefers-color-scheme: light)",
        url: `${getPublicPrefix()}/assets_logo/ai_arena_logo_icon_03_9mn_icon.ico`,
      },
    ],
  },
};

export default function ServerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const faviconUrl = `${getPublicPrefix()}/assets_logo/img/favicon.ico`;

  return (
    <html lang="en">
      <head>
        <link rel="icon" href={faviconUrl} sizes="any" />
      </head>
      <body
        className={`${quicksand.variable} ${gugi.variable} font-sans text-center`}
      >
        <BackgroundTexture>
          <ClientWrapper>
            {children}
            </ClientWrapper>
        </BackgroundTexture>
      </body>
    </html>
  );
}
