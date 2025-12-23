import { graphql, useLazyLoadQuery } from "react-relay";
import { AuthNavbarQuery } from "./__generated__/AuthNavbarQuery.graphql";
import { NavLink } from "react-router";
import clsx from "clsx";

export default function AuthNavbar() {
  const data = useLazyLoadQuery<AuthNavbarQuery>(
    graphql`
      query AuthNavbarQuery {
        viewer {
          user {
            id
          }
        }
      }
    `,
    {}
  );

  return (
    <li key={"authentication"} className="pb-2 text-l p-2 text-center">
      {data.viewer?.user ? (
        <NavLink
          key={"dashboard"}
          to={"/dashboard"}
          className={({ isActive }) =>
            clsx(
              "py-2 text-white border-b-2",
              isActive
                ? "border-customGreen"
                : "border-transparent hover:border-customGreen"
            )
          }
        >
          Dashboard
        </NavLink>
      ) : (
        <a
          key={"login"}
          href={"/accounts/login/"}
          className={clsx(
            "py-2 text-white border-b-2",
            window.location.pathname === "/accounts/login/"
              ? "border-customGreen"
              : "border-transparent hover:border-customGreen"
          )}
        >
          Login
        </a>
      )}
    </li>
  );
}
