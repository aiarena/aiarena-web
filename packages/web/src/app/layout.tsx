import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });



function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
     
        <body className={`${inter.className} text-center`}>
  
            {children}

        </body>
  
    </html>
  );
}

export default RootLayout;
