// import NextAuthSessionProvider from "./../components/providers/NextAuthSessionProvider";
// import Navbar from "@/components/_nav/Navbar";

import Footer from "@/_components/_nav/Footer";
import Navbar from "@/_components/_nav/Navbar";
import { useUserContext } from "@/_components/providers/UserProvider";
import { redirect } from "next/navigation"; // Import the redirect helper

export const metadata = {
  title: "AI Arena Profile",
  description: "Your AI arena dashboard to manage bots.",
};

function Layout({ children }: { children: React.ReactNode }) {
  // const router = useRouter();
  // const { user, setUser, fetching } = useUserContext();
  
  // if (user === null && fetching === false) {
  //   redirect("/");
  // }
  // if (user === null) {
  //   return;
  // }

  return (
    <>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow  bg-darken">{children}</main>
        <Footer />
      </div>
    </>
  );
}

export default Layout;
