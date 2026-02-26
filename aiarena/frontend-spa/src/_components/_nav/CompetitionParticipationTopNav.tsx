import clsx from "clsx";
import { ReactNode } from "react";
import { NavLink, Outlet } from "react-router";

type TopTab = {
  name: string;
  to: string;
};

export default function CompetitionParticipationTopNav({
  pages,
  children,
}: {
  pages: TopTab[];
  children?: ReactNode;
}) {
  return (
    <div>
      <div className="w-full pb-2">
        {pages.map((tab) => (
          <NavLink
            key={tab.name}
            to={tab.to}
            className={({ isActive }) =>
              clsx(
                "m-1 px-4 py-2 text-white border-1 bg-darken-2 shadow-black shadow-sm duration-300 ease-in-out transform backdrop-blur-sm text-center",
                "inline-flex items-center justify-center no-underline select-none cursor-pointer appearance-none",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-customGreen focus-visible:ring-offset-2 focus-visible:ring-offset-transparent",

                isActive
                  ? "text-large border-neutral-700 border-b-customGreen border-b-2"
                  : "border-neutral-700 hover:border-b-customGreen border-b-2",
              )
            }
          >
            <p className="text-gray-100 text-l text-center">{tab.name}</p>
          </NavLink>
        ))}
      </div>

      <main role="main">{children ?? <Outlet />}</main>
    </div>
  );
}
