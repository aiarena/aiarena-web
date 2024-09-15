"use client"
import { useUser } from '@/_components/_hooks/useUser'; // Assuming your hook is here
import { useSignOut } from '@/_components/_hooks/useSignOut'; // Assuming your hook is here
import { useRouter } from 'next/navigation';
import {useUserContext} from "@/_components/providers/UserProvider";

export default function Page() {

  const [signOut, isSigningOut] = useSignOut(); // SignOut mutation and loading state
  const router = useRouter(); // Next.js router for navigation
    const {user, setUser } = useUserContext()

  // Handle sign out and redirect
  const handleSignOut = () => {
    signOut(); // Trigger the sign out mutation
      setUser(null);
    router.push("/"); // Redirect to /profile after sign out
  };

  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold">Display a JWT authorized profile</h1>
      <p className="text-lg mt-4">Protected Page!</p>
      <p>Logged in as {user?.id}</p>
      <button onClick={handleSignOut} disabled={isSigningOut} className={"bg-red-500"}>
        {isSigningOut ? "Signing Out..." : "Log Out"}
      </button>
    </div>
  );
}
