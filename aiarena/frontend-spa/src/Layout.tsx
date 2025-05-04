import { Outlet } from "react-router";
import Navbar from "./_components/_nav/Navbar";
import Footer from "./_components/_nav/Footer";
import BackgroundTexture from "./_components/_display/BackgroundTexture";
import WithSideNav from "./_components/_nav/WithSideNav";

export default function Layout() {
  return (
    <BackgroundTexture>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <WithSideNav>
          <Outlet />
        </WithSideNav>
        <Footer />
      </div>
    </BackgroundTexture>
  );
}
