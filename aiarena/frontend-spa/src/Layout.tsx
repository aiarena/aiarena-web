import { Outlet } from "react-router";
import Navbar from "./_components/_nav/Navbar";
import Footer from "./_components/_nav/Footer";

export default function Layout() {
  return (
    <div className="flex flex-col min-h-screen font-sans text-custom-green ">
      <Navbar />
      <div className="text-black"> asd</div>
      <main className="flex-grow bg-warmGray">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
