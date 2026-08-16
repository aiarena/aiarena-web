import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { NavLink, Navigate, Outlet } from "react-router";
import clsx from "clsx";

import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

import { AdminLayoutQuery } from "./__generated__/AdminLayoutQuery.graphql";

function AdminLayoutContent() {
  const data = useLazyLoadQuery<AdminLayoutQuery>(
    graphql`
      query AdminLayoutQuery {
        viewer {
          isSuperuser
          user {
            id
            username
          }
        }
      }
    `,
    {},
  );

  if (!data.viewer?.user) {
    window.location.replace("/accounts/login/");
    return null;
  }

  if (!data.viewer.isSuperuser) {
    return (
      <div className="mx-auto max-w-3xl py-16">
        <div className="rounded-2xl border border-neutral-800 bg-darken-2 p-8 text-center shadow-xl backdrop-blur-lg">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-xl text-red-400">
            ✕
          </div>

          <h1 className="text-xl font-semibold text-neutral-100">
            Admin access required
          </h1>

          <p className="mt-2 text-sm text-neutral-400">
            Your account does not have permission to access the administration
            area.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
      <div className="overflow-hidden rounded-2xl border border-neutral-800 bg-darken-2 shadow-xl backdrop-blur-lg">
        <div className="border-b border-neutral-800 px-6 py-5">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-100">
                Administration
              </h1>

              <p className="mt-1 text-sm text-neutral-400">
                Site administration and operational tools.
              </p>
            </div>

            <div className="mt-3 text-sm text-neutral-500 sm:mt-0">
              Signed in as{" "}
              <span className="font-medium text-neutral-300">
                {data.viewer.user.username}
              </span>
            </div>
          </div>
        </div>

        <nav className="flex overflow-x-auto px-3">
          <AdminNavLink to="/management/statistics">Statistics</AdminNavLink>
          <AdminNavLink to="/management/competitions">
            Competitions
          </AdminNavLink>
        </nav>
      </div>

      <Outlet />
    </div>
  );
}

interface AdminNavLinkProps {
  to: string;
  children: React.ReactNode;
}

function AdminNavLink({ to, children }: AdminNavLinkProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        clsx(
          "relative whitespace-nowrap px-4 py-4 text-sm font-medium transition-colors",
          isActive ? "text-white" : "text-neutral-400 hover:text-neutral-200",
        )
      }
    >
      {({ isActive }) => (
        <>
          {children}

          {isActive && (
            <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-customGreen" />
          )}
        </>
      )}
    </NavLink>
  );
}

export default function AdminLayout() {
  return (
    <ErrorBoundaryWrapper>
      <Suspense fallback={<DisplaySkeleton height={558} />}>
        <AdminLayoutContent />
      </Suspense>
    </ErrorBoundaryWrapper>
  );
}
