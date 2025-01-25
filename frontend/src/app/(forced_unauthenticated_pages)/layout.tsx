// import NextAuthSessionProvider from "./../components/providers/NextAuthSessionProvider";
// import Navbar from "@/components/_nav/Navbar";
"use client"
import Footer from "@/_components/_nav/Footer";
import Navbar from "@/_components/_nav/Navbar";
import { useUserContext } from "@/_components/providers/UserProvider";
import { Exo_2 } from "next/font/google";
import { useRouter } from "next/navigation";
import { useEffect } from "react";


function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { user,  fetching } = useUserContext();
  
  useEffect(() => {
    if (user !== null && fetching === false) {
      console.log(user, fetching)
      router.push("/profile/");
    }
  }, [user,fetching, router])
  


  return (
    <>
      <div
        className="flex flex-col min-h-screen bg-background-texture"
        style={{ backgroundImage: `url('${process.env.PUBLIC_PREFIX}/backgrounds/background.gif')` }}
      >
        <Navbar />
      
        <main className="flex-grow  bg-darken">{!fetching ? children : <></>}</main>
       
        <Footer />
      </div>
    </>
  );
}


export default Layout;
