import { sideNavbarLinks } from "@/_data/sideNavbarLinks";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { NavLink } from "react-router";
import clsx from "clsx";

export default function WithSideNav({ children }: { children: ReactNode }) {
  const [sideNavbar, setSideNavbar] = useState(false);
  const [navbarHeight, setNavbarHeight] = useState(0);

  const handleWindowResize = useCallback(() => {
    if (window.innerWidth >= 1024) {
      setSideNavbar(true);
    } else {
      setSideNavbar(false);
    }
  }, []);

  useEffect(() => {
    const calculateNavbarHeight = () => {
      const navbar = document.querySelector("nav");
      if (navbar) {
        setNavbarHeight(navbar.offsetHeight);
      }
    };

    calculateNavbarHeight();
    handleWindowResize();

    const handleResizeWithNavbar = () => {
      handleWindowResize();
      calculateNavbarHeight();
    };

    const navbar = document.querySelector("nav");
    let resizeObserver: ResizeObserver | null = null;

    if (navbar) {
      resizeObserver = new ResizeObserver(() => {
        calculateNavbarHeight();
      });
      resizeObserver.observe(navbar);
    }

    window.addEventListener("resize", handleResizeWithNavbar);

    return () => {
      window.removeEventListener("resize", handleResizeWithNavbar);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [handleWindowResize]);

  return (
    <div className={clsx(sideNavbar && "flex")}>
      {sideNavbar ? (
        <aside className="w-1/12 min-w-[12em] bg-darken-2 border-r border-neutral-700">
          <div
            className="sticky flex flex-col"
            style={{ top: `${navbarHeight}px` }}
          >
            {sideNavbarLinks.map((tab) => (
              <NavLink
                key={tab.name}
                to={tab.path}
                className={({ isActive }) =>
                  clsx(
                    "m-2 pl-2 py-2 text-white border-1 shadow-black shadow-sm hover:shadow-customGreen-dark duration-300 ease-in-out transform backdrop-blur-sm",
                    isActive
                      ? "text-large border-neutral-700 border-b-customGreen border-b-2"
                      : "border-neutral-700 hover:border-b-customGreen border-b-2"
                  )
                }
              >
                <p className="text-gray-100 text-l">{tab.name}</p>
              </NavLink>
            ))}
          </div>
        </aside>
      ) : (
        <div
          className="sticky z-49 border-b border-customGreen"
          style={{ top: `${navbarHeight}px` }}
        >
          <div className="flex flex-wrap justify-center space-x-4 py-4 bg-black">
            {sideNavbarLinks.map((tab) => (
              <NavLink
                key={tab.name}
                to={tab.path}
                className={({ isActive }) =>
                  clsx(
                    "py-2 text-white font-gugi",
                    isActive
                      ? "border-b-2 border-customGreen"
                      : "border-b-2 border-transparent hover:border-customGreen"
                  )
                }
              >
                {tab.name}
              </NavLink>
            ))}
          </div>
        </div>
      )}

      <main
        className={clsx(
          sideNavbar ? "flex-1" : "sticky top-0",
          "overflow-y-auto p-8 min-h-[90vh]"
        )}
        role="main"
      >
        {children}
      </main>
    </div>
  );
}
