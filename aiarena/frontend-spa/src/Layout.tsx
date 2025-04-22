import { Outlet } from "react-router";
import Navbar from "./_components/_nav/Navbar";
import Footer from "./_components/_nav/Footer";
import BackgroundTexture from "./_components/BackgroundTexture";

export default function Layout() {
  return (
    <BackgroundTexture>
      <div className="flex flex-col min-h-screen ">
        <Navbar />
        <div className="p-10 space-y-4">
          <p className="text-xl font-quicksand">This is Quicksand</p>
          <p className="text-xl font-gugi">This is Gugi</p>
          <p className="text-xl font-sans">This is default sans-serif</p>
        </div>
        <main className="flex-grow bg-warmGray">
          <Outlet />
        </main>
        <Footer />
      </div>
    </BackgroundTexture>
  );
}
