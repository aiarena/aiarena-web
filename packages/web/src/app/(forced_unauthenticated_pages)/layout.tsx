// import NextAuthSessionProvider from "./../components/providers/NextAuthSessionProvider";
// import Navbar from "@/components/_nav/Navbar";
"use client"
import Footer from "@/_components/_nav/Footer";
import Navbar from "@/_components/_nav/Navbar";


// export const metadata = {
//   title: "SST - Next.js Starter",
//   description: "Serverless Next.js deployment with Auth, S3 and DynamoDB",
// };

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Navbar />
      {children}
      <Footer/>
    </>
  );
}


export default Layout;
