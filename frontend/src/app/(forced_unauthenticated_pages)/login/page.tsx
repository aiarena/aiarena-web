"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSignIn } from "@/_components/_hooks/useSignIn";
import { useUserContext } from "@/_components/providers/UserProvider";
import { fetchUser } from "@/_lib/fetchUser";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const [signIn, isSigningIn, signInError] = useSignIn();
  const { setUser, fetching } = useUserContext();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    signIn(username, password, async () => {
      try {
        const user = await fetchUser(); 
        setUser(user);
        router.push("/profile");
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    });
  };

  return (
    <div className="flex flex-col min-h-screen justify-center items-center text-white">
      <form
        onSubmit={handleLogin}
        className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md"
      >
        <h1 className="text-2xl font-bold mb-6">Login</h1>

        {signInError && (
          <p className="mb-4 text-red-500">Error: {signInError}</p>
        )}

        <label htmlFor="username" className="block mb-2">
          Username
        </label>
        <input
          id="username"
          name="username"
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="w-full p-2 mb-4 text-black rounded"
        />

        <label htmlFor="password" className="block mb-2">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full p-2 mb-4 text-black rounded"
        />

        <button
          type="submit"
          disabled={isSigningIn || fetching}
          className="w-full bg-customGreen text-black p-2 rounded"
        >
          {isSigningIn ? "Logging in..." : "Login"}
        </button>
      
        <div className="mt-4 text-center">
          <a href="/register" className="text-softTeal hover:underline">
            Register Here
          </a>
        </div>

        <div className="mt-4 text-center">
          {/* Add a link to the recover page */}
          <a href="/recover" className="text-softTeal hover:underline">
            Forgot Username or Password?
          </a>
        </div>
      </form>
    </div>
  );
}
