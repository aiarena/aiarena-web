import { sideNavbarLinks } from "@/_data/sideNavbarLinks";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { NavLink } from "react-router";

export default function WithSideNav({ children }: { children: ReactNode }) {
  const [sideNavbar, setSideNavbar] = useState(false);

  // one stable, memoised function
  const handleWindowResize = useCallback(() => {
    if (window.innerWidth >= 920) {
      setSideNavbar(true); // close on large screens
    } else {
      setSideNavbar(false);
    }
  }, []); // ︙no deps → same reference for life

  useEffect(() => {
    // run once so the initial state matches the viewport
    handleWindowResize();

    window.addEventListener("resize", handleWindowResize);
    return () => window.removeEventListener("resize", handleWindowResize);
  }, [handleWindowResize]); // <- handler is now stable, so it’s safe

  return (
    <div className={`${sideNavbar ? "flex" : ""}`}>
      {sideNavbar ? (
        <aside className="w-1/8 min-w-[200px] bg-gray-900 text-gray-100 flex flex-col">
          {sideNavbarLinks.map((tab) => (
            <NavLink
              key={tab.name}
              to={tab.path}
              className={({ isActive }) =>
                `m-2 pl-2 py-2 text-white border-b-2  ${
                  isActive
                    ? "bg-gray-800 text-large border-customGreen"
                    : "border-gray-800 border-b-transparent hover:border-customGreen"
                }`
              }
            >
              {tab.name}
            </NavLink>
          ))}
        </aside>
      ) : (
        <div className="border-b border-customGreen">
          <div className="flex flex-wrap justify-center space-x-4 py-4 bg-gray-900">
            {sideNavbarLinks.map((tab) => (
              <NavLink
                key={tab.name}
                to={tab.path}
                className={({ isActive }) =>
                  `py-2 text-white  ${
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
        className={`${sideNavbar ? "flex-1" : ""} overflow-y-auto  p-8 bg-darken min-h-[90vh]`}
      >
        {children}
      </main>
    </div>
  );
}
