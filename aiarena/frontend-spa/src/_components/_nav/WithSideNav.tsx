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
        <aside className="w-1/12 min-w-[12em] bg-gray-900 flex flex-col border-r border-gray-700">
          {sideNavbarLinks.map((tab) => (
            <NavLink
              key={tab.name}
              to={tab.path}
              className={({ isActive }) =>
                `m-2 pl-2 py-2 text-white border-1 font-gugi shadow shadow-black shadow-sm hover:shadow-md hover:shadow-black sduration-300 ease-in-out transform   ${
                  isActive
                    ? "bg-gray-800 text-large border-gray-700 border-b-customGreen border-b-2"
                    : "border-gray-700 hover:border-b-customGreen border-b-2"
                }`
              }
            >
              <p className="text-gray-100 font-thin text-l"> {tab.name}</p>
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
