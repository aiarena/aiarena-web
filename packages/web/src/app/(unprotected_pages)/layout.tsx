// import NextAuthSessionProvider from "./../components/providers/NextAuthSessionProvider";
// import Navbar from "@/components/_nav/Navbar";
"use client"
import Navbar from "@/_components/_nav/Navbar";



function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}


export default Layout;
