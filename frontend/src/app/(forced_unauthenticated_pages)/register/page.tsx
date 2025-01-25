"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Implement your registration logic here
      console.log("Registering:", { email, password });

      // On success, redirect to the login page
      router.push("/login");
    } catch (error) {
      console.error("Registration failed:", error);
    }
  };

  return (
    <div className="flex flex-col min-h-screen justify-center items-center text-white">
      <form
        onSubmit={handleRegister}
        className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md"
      >
        <h1 className="text-2xl font-bold mb-6">Register</h1>

        <label htmlFor="email" className="block mb-2">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          className="w-full bg-customGreen text-black p-2 rounded"
        >
          Register
        </button>

        <div className="mt-4 text-center">
          <a href="/login" className="text-softTeal hover:underline">
            Back to Login
          </a>
        </div>
      </form>
    </div>
  );
}
