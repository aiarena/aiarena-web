import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

// export const metadata = {
//   title: "SST - Next.js Starter",
//   description: "Serverless Next.js deployment with Auth, S3 and DynamoDB",
// };

function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
     
        <body className={inter.className}>
          {/* <AuthProvider> */}
            {children}
            {/* </AuthProvider> */}
        </body>
  
    </html>
  );
}

export default RootLayout;
