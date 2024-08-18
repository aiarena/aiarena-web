"use client";
export const dynamic = "force-dynamic";
import { useEffect, useState } from "react";

import Link from "next/link";
// import { useAuth } from "../../providers/AuthProvider";
// import { signOut } from "next-auth/react";
// import { useSession } from "next-auth/react";

export default function AuthNavBar() {
  // const session = useSession();

  // const handleLogout = () => {
  //   signOut();
  // };

  return (
    <div className="container flex items-center justify-center p-1">
      {/* {session.status === "authenticated" ? (
        <button
          onClick={handleLogout}
          className="bg-red-500 rounded py-1 px-2 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Log Out
        </button>
      ) : ( */}
        <>
          {/* {session.status === "loading" ? (
            <div className="bg-slate-400 rounded py-4 px-8"> </div>
          ) : ( */}
            <div className="mt-1">
              <Link href="/signup">
                <span className="bg-green-500 m-2 rounded py-1 px-2">
                  Sign Up
                </span>
              </Link>
              <Link href="/auth/signin">
                <span className="bg-green-500 m-2 rounded py-1 px-2">
                  Log In
                </span>
              </Link>
            </div>
          {/* )} */}
        </>
      {/* )} */}
    </div>
  );
}
