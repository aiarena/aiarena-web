import { Outlet, useLocation } from "react-router";
import Navbar from "./_components/_nav/Navbar";
import Footer from "./_components/_nav/Footer";
import BackgroundTexture from "./_components/_display/BackgroundTexture";
import WithSideNav from "./_components/_nav/WithSideNav";
import { useEffect } from "react";

function scrollToHashWithOffset(offset = -40) {
  if (!window.location.hash) return;

  const id = window.location.hash.slice(1);
  const el = document.getElementById(id);
  if (!el) return;

  const rect = el.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const top = rect.top + scrollTop + offset;

  window.scrollTo({
    top,
    behavior: "smooth",
  });
}

export default function Layout() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    if (!hash) {
      window.scrollTo(0, 0);
    }
    scrollToHashWithOffset(-400);
  }, [pathname, hash]);

  return (
    <BackgroundTexture>
      <div className="flex flex-col min-h-screen font-quicksand ">
        <Navbar />
        <WithSideNav>
          <Outlet />
        </WithSideNav>
        <Footer />
      </div>
    </BackgroundTexture>
  );
}
