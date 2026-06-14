import { graphql, useLazyLoadQuery } from "react-relay";
import { AuthNavbarQuery } from "./__generated__/AuthNavbarQuery.graphql";
import { NavLink } from "react-router";
import clsx from "clsx";
import { reverseUrl } from "@/_lib/reverseUrl";

interface AuthNavbarProps {
  mobile?: boolean;
}

export default function AuthNavbar({ mobile = false }: AuthNavbarProps) {
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
    {},
  );

  const baseClasses = mobile
    ? "block w-full bg-darken-3 hover:bg-darken-4 py-2 text-white hover:text-slate-300 border-b-2"
    : "py-2 text-white border-b-2";

  const activeBorder = "border-customGreen";
  const inactiveBorder = mobile
    ? "border-transparent"
    : "border-transparent hover:border-customGreen";

  return (
    <li>
      {data.viewer?.user ? (
        <NavLink
          to={reverseUrl("dashboard_root")}
          className={({ isActive }) =>
            clsx(baseClasses, isActive ? activeBorder : inactiveBorder)
          }
        >
          Dashboard
        </NavLink>
      ) : (
        <a
          href={reverseUrl("login")}
          className={clsx(
            baseClasses,
            window.location.pathname === reverseUrl("login")
              ? activeBorder
              : inactiveBorder,
          )}
        >
          Login
        </a>
      )}
    </li>
  );
}
