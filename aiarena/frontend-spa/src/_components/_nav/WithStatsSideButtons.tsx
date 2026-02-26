import { statsSideNavbarLinks } from "@/_pages/Rework/CompetitionParticipation/StatsSideNavbarLinks";
import clsx from "clsx";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { NavLink } from "react-router";

export default function WithStatsSideButtons({
  children,
}: {
  children: ReactNode;
}) {
  const [sideNavbar, setSideNavbar] = useState(false);
  const handleWindowResize = useCallback(() => {
    if (window.innerWidth >= 1024) {
      setSideNavbar(true);
    } else {
      setSideNavbar(false);
    }
  }, []);

  useEffect(() => {
    handleWindowResize();

    const handleResizeWithNavbar = () => {
      handleWindowResize();
    };

    const navbar = document.querySelector("nav");
    let resizeObserver: ResizeObserver | null = null;

    if (navbar) {
      resizeObserver = new ResizeObserver(() => {});
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
    <div>
      {" "}
      <div className={clsx(sideNavbar && "flex")}>
        {sideNavbar ? (
          <aside className="ml-2 w-1/12 min-w-[12em]  mt-4">
            <div className="sticky flex flex-col">
              {statsSideNavbarLinks.map((tab) => (
                <NavLink
                  key={tab.name}
                  to={tab.state}
                  relative="path"
                  className={({ isActive }) =>
                    clsx(
                      "my-1  mr-2 pl-2 py-2 text-white border-1 bg-darken-2 shadow-black shadow-sm  duration-300 ease-in-out transform backdrop-blur-sm",
                      isActive
                        ? "text-large border-neutral-700 border-b-customGreen border-b-2"
                        : "border-neutral-700 hover:border-b-customGreen border-b-2",
                    )
                  }
                >
                  <p className="text-gray-100 text-l">{tab.name}</p>
                </NavLink>
              ))}
            </div>
          </aside>
        ) : (
          <div className="sticky z-49 border-b border-customGreen">
            <div className="flex flex-wrap justify-center space-x-4 py-4 bg-darken-2">
              {statsSideNavbarLinks.map((tab) => (
                <NavLink
                  key={tab.name}
                  to={tab.state}
                  relative="path"
                  className={({ isActive }) =>
                    clsx(
                      "py-2 text-white font-gugi",
                      isActive
                        ? "border-b-2 border-customGreen"
                        : "border-b-2 border-transparent hover:border-customGreen",
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
            "overflow-y-auto",
            "mt-4",
          )}
          role="main"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
