import { Outlet } from "react-router";
import Navbar from "./_components/_nav/Navbar";
import Footer from "./_components/_nav/Footer";
import BackgroundTexture from "./_components/_display/BackgroundTexture";
import clsx from "clsx";
export default function RootLayout() {
  return (
    <BackgroundTexture>
      <div className="flex flex-col min-h-screen font-quicksand">
        <Navbar />

        <main
          className={clsx("flex-1 overflow-y-auto p-8 min-h-[90vh]")}
          role="main"
        >
          <Outlet />
        </main>

        <Footer />
      </div>
    </BackgroundTexture>
  );
}
