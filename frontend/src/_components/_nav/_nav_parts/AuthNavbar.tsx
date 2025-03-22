"use client";

export const dynamic = "force-dynamic";

import Link from "next/link";
import { useSignOut } from "@/_components/_hooks/useSignOut";
import { useViewerContext } from "@/_components/providers/ViewerProvider";
import { useRouter } from "next/navigation";

export default function AuthNavBar() {
  const router = useRouter(); // Next.js router for navigation
  const { viewer, setViewer, fetching } = useViewerContext();
  const [signOut] = useSignOut();

  const handleSignOut = () => {
    signOut(); // Trigger the sign out mutation
    setViewer(null);
    router.push("/"); // Redirect to /profile after sign out
  };

  if (fetching) {
    return (
      <div className="container flex items-center justify-center p-1 ">
        <span className="py-1 px-2 text-gray-500">Loading</span>
      </div>
    );
  }

  return (
    <div className="container flex items-center justify-center p-1">
      {viewer ? (
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
              Login
            </span>
          </Link>
        </div>
      )}
    </div>
  );
}
