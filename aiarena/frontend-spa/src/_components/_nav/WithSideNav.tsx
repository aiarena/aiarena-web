import { sideNavbarLinks } from "@/_data/sideNavbarLinks";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { NavLink } from "react-router";

export default function WithSideNav({ children }: { children: ReactNode }) {
  const [sideNavbar, setSideNavbar] = useState(false);
  const [navbarHeight, setNavbarHeight] = useState(0);

  const handleWindowResize = useCallback(() => {
    if (window.innerWidth >= 920) {
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
    <div className={`${sideNavbar ? "flex" : ""}`}>
      {sideNavbar ? (
        <aside className="w-1/12 min-w-[12em] bg-gray-900 border-r border-gray-700">
          <div
            className="sticky flex flex-col"
            style={{ top: `${navbarHeight}px` }}
          >
            {sideNavbarLinks.map((tab) => (
              <NavLink
                key={tab.name}
                to={tab.path}
                className={({ isActive }) =>
                  `m-2 pl-2 py-2 text-white border-1 shadow shadow-black shadow-sm hover:shadow-md hover:shadow-black duration-300 ease-in-out transform ${
                    isActive
                      ? "bg-gray-800 text-large border-gray-700 border-b-customGreen border-b-2"
                      : "border-gray-700 hover:border-b-customGreen border-b-2"
                  }`
                }
              >
                <p className="text-gray-100 text-l">{tab.name}</p>
              </NavLink>
            ))}
          </div>
        </aside>
      ) : (
        <div
          className="sticky z-50
        border-b border-customGreen"
          style={{ top: `${navbarHeight}px` }}
        >
          <div className="flex flex-wrap justify-center space-x-4 py-4 bg-gray-900">
            {sideNavbarLinks.map((tab) => (
              <NavLink
                key={tab.name}
                to={tab.path}
                className={({ isActive }) =>
                  `py-2 text-white font-gugi ${
                    isActive
                      ? "border-b-2 border-customGreen"
                      : "border-b-2 border-transparent hover:border-customGreen"
                  }`
                }
              >
                {tab.name}
              </NavLink>
            ))}
          </div>
        </div>
      )}

      <main
        className={`${sideNavbar ? "flex-1" : "sticky top-0"} overflow-y-auto p-8 bg-darken min-h-[90vh]`}
      >
        {children}
      </main>
    </div>
  );
}
