"use client";
import { useUser } from "@/_components/_hooks/useUser";

export const dynamic = "force-dynamic";
import { useEffect, useState } from "react";

import Link from "next/link";
import { useLogin } from "@/_components/providers/LoginProvider";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useUserContext } from "@/_components/providers/UserProvider";
import { useRouter } from "next/navigation";


export default function AuthNavBar() {

  const router = useRouter(); // Next.js router for navigation
  const { user, setUser } = useUserContext();
  const [signOut, isSigningOut] = useSignOut();

  const handleSignOut = () => {
    signOut(); // Trigger the sign out mutation
    setUser(null);
    router.push("/"); // Redirect to /profile after sign out
  };

  return (
    <div className="container flex items-center justify-center p-1">
      {user ? (
        <button
          onClick={handleSignOut}
          className="bg-red-500 rounded py-1 px-2 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Log Out
        </button>
      ) : (
        <div className="mt-1">
          <Link href="/register">
            <span className="bg-customGreen m-2 rounded py-1 px-2 whitespace-nowrap">
              Sign Up
            </span>
          </Link>

          <Link href="/login">
            <span className="bg-customGreen m-2 rounded py-1 px-2 whitespace-nowrap">
              Log in
            </span>
          </Link>
        </div>
      )}
    </div>
  );
}
