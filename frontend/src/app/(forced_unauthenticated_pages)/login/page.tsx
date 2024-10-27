"use client";
import {useState, useEffect} from "react";
import {useRouter} from "next/navigation";
import {useSignIn} from "@/_components/_hooks/useSignIn";
import {useUser} from "@/_components/_hooks/useUser";
import {useSignOut} from "@/_components/_hooks/useSignOut";
import {useUserContext} from "@/_components/providers/UserProvider";
import {fetchUser} from "@/_lib/fetchUser";

export default function Page() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [showRegister, setShowRegister] = useState(false);
    const [showForgotUsername, setShowForgotUsername] = useState(false);

    const router = useRouter(); // Next.js router for redirection
    const [signIn, isSigningIn, signInError] = useSignIn();
    const [signedIn, setSignedIn] = useState(false); // New state to trigger user refetch

    const {setUser} = useUserContext();

    const handleLogin = () => {
        signIn(username, password, () => {
            setSignedIn(true);
        });

    };

 // Fetch user data after successful sign-in
  useEffect(() => {
    if (signedIn) {
      // Declare an async function inside the useEffect
      const fetchAndSetUser = async () => {
        try {
          const user = await fetchUser(); // Await the user data
            console.log("user",user)
          setUser(user); // Update the global user context with the fetched user data
          router.push('/profile'); // Redirect to profile page
        } catch (error) {
          console.error('Failed to fetch user:', error);
        }
      };

      fetchAndSetUser(); // Call the async function
    }
  }, [signedIn, setUser, router]); // Refetch user after successful login

    return (
        <div className="flex flex-col min-h-screen font-sans text-white">

            <main className="flex-grow flex justify-center items-center">
                <div className="bg-gray-900 p-8 rounded-lg shadow-lg w-full max-w-md">
                    {!showRegister && !showForgotUsername && (
                        <div>
                            <h2 className="text-2xl font-bold mb-4">Login</h2>

                            {signInError && (
                                <div className="mb-4 text-red-500">
                                    {signInError}
                                </div>
                            )}

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
                                disabled={isSigningIn}
                                className="w-full bg-customGreen text-black p-2 rounded"
                            >
                                {isSigningIn ? "Logging in..." : "Login"}
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

                    {/* Registration Form */}
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
                            {/*<button*/}
                            {/*  onClick={() => handleRegister()}*/}
                            {/*  className="w-full bg-mellowYellow text-black p-2 rounded"*/}
                            {/*>*/}
                            {/*  Register*/}
                            {/*</button>*/}
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

                    {/* Forgot Username Form */}
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
                            {/*<button*/}
                            {/*  onClick={handleForgotUsername}*/}
                            {/*  className="w-full bg-softTeal text-black p-2 rounded"*/}
                            {/*>*/}
                            {/*  Recover Username*/}
                            {/*</button>*/}
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
