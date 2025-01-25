"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RecoverPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const router = useRouter();

  const handleRecover = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Replace this with actual recovery logic (API call)
      console.log("Recover request submitted for email:", email);
      setSubmitted(true); // Show confirmation message
    } catch (error) {
      console.error("Recovery failed:", error);
    }
  };

  return (
    <div className="flex flex-col min-h-screen justify-center items-center text-white">
      <form
        onSubmit={handleRecover}
        className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md"
      >
        {!submitted ? (
          <>
            <h1 className="text-2xl font-bold mb-6">Recover Account</h1>

            <label htmlFor="email" className="block mb-2">
              Email Address
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

            <button
              type="submit"
              className="w-full bg-customGreen text-black p-2 rounded"
            >
              Recover Account
            </button>

            <div className="mt-4 text-center">
              <a
                href="/login"
                className="text-softTeal hover:underline"
              >
                Back to Login
              </a>
            </div>
          </>
        ) : (
          <div className="text-center">
            <h2 className="text-xl font-bold mb-4">Recovery Email Sent</h2>
            <p className="mb-4">
              If this email is associated with an account, you will receive recovery instructions shortly.
            </p>
            <button
              type="button"
              onClick={() => router.push("/login")}
              className="w-full bg-customGreen text-black p-2 rounded"
            >
              Back to Login
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
