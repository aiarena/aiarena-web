"use client";
import {LoginProvider} from "@/_components/providers/LoginProvider";
import "./globals.css";
import {Inter} from "next/font/google";
import {Quicksand} from "next/font/google";
import {Gugi} from "next/font/google";
import RelayEnvironment from "@/_lib/RelayEnvironment";
import {RelayEnvironmentProvider} from "react-relay";
import {UserProvider} from "@/_components/providers/UserProvider";
import { quicksand, gugi } from "@/_styles/fonts"; // Adjust the path as necessary


const inter = Inter({subsets: ["latin"]});

function RootLayout({children}: { children: React.ReactNode }) {
    return (
        <html lang="en">
        <body
          className={`${quicksand.variable} ${gugi.variable} font-sans text-center  bg-background-texture`}
          style={{ backgroundImage: `url('${process.env.PUBLIC_PREFIX}/backgrounds/background.gif')` }}
        >
        <RelayEnvironmentProvider environment={RelayEnvironment}>
            <LoginProvider>
                <UserProvider>
                    {children}
                </UserProvider>
            </LoginProvider>
        </RelayEnvironmentProvider>
        </body>
        </html>
    );
}

export default RootLayout;