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
                isActive
                  ? "m-2 bg-gray-800 pl-2 py-2 text-white text-large border-b-2 border-customGreen"
                  : "m-2 border-gray-800 pl-2 py-2 text-white border-b-2 border-b-transparent hover:border-customGreen"
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
              <a
                key={tab.name}
                href={tab.path}
                className={`py-2 text-white  ${
                  window.location.pathname === tab.path
                    ? "border-b-2 border-customGreen"
                    : "border-b-2 border-transparent hover:border-customGreen"
                }`}
              >
                {tab.name}
              </a>
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
