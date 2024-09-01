"use client";
import { pages } from "next/dist/build/templates/app-page";
import Image from "next/image";
import React, { useState } from "react";

// export const dynamic = "force-dynamic";
export default function Page() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [showForgotUsername, setShowForgotUsername] = useState(false);

  const handleLogin = () => {
    alert(`Logged in with username: ${username} and password: ${password}`);
  };

  const handleRegister = () => {
    alert(`Registered with email: ${email} and password: ${password}`);
  };

  const handleForgotUsername = () => {
    alert(`Username recovery for email: ${email}`);
  };
  return (
    <div className="flex flex-col min-h-screen font-sans  text-white">
  

      <main className="flex-grow flex justify-center items-center">
        <div className="bg-gray-900 p-8 rounded-lg shadow-lg w-full max-w-md">
          {!showRegister && !showForgotUsername && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Login</h2>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full p-2 mb-4 text-black"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2 mb-4 text-black"
              />
              <button
                onClick={handleLogin}
                className="w-full bg-customGreen text-black p-2 rounded"
              >
                Login
              </button>
              <div className="mt-4 text-center">
                <a
                  href="#"
                  className="text-softTeal hover:underline"
                  onClick={() => setShowForgotUsername(true)}
                >
                  Forgot Username?
                </a>
              </div>
              <div className="mt-2 text-center">
                <a
                  href="#"
                  className="text-softTeal hover:underline"
                  onClick={() => setShowRegister(true)}
                >
                  Register Here
                </a>
              </div>
            </div>
          )}

          {showRegister && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Register</h2>
              <input
                type="text"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-2 mb-4 text-black"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2 mb-4 text-black"
              />
              <button
                onClick={handleRegister}
                className="w-full bg-mellowYellow text-black p-2 rounded"
              >
                Register
              </button>
              <div className="mt-4 text-center">
                <a
                  href="#"
                  className="text-softTeal hover:underline"
                  onClick={() => setShowRegister(false)}
                >
                  Back to Login
                </a>
              </div>
            </div>
          )}

          {showForgotUsername && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Forgot Username</h2>
              <input
                type="text"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-2 mb-4 text-black"
              />
              <button
                onClick={handleForgotUsername}
                className="w-full bg-softTeal text-black p-2 rounded"
              >
                Recover Username
              </button>
              <div className="mt-4 text-center">
                <a
                  href="#"
                  className="text-mellowYellow hover:underline"
                  onClick={() => setShowForgotUsername(false)}
                >
                  Back to Login
                </a>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}