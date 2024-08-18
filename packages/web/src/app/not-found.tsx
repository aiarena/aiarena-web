"use client";
import React, { useEffect } from "react";
import Navbar from "@/_components/_nav/Navbar";
import Footer from "@/_components/_nav/Footer";
import Link from "next/link";

function Page() {
  // const { data: session, status } = useSession();
  // console.log(session);
  // useEffect(() => {
  //   console.log(session);
  // }, [session]);

  return (
    <>
      <Navbar />
      <div className="flex flex-col items-center justify-center min-h-screen text-center">
        <h1 className="text-9xl font-extrabold  tracking-widest">
          404
        </h1>
        <div className="bg-customGreen px-2 text-sm rounded rotate-12 absolute top-1/2">
          Page Not Found
        </div>
        <p className="text-lg mt-4  mb-10">
          Sorry, we couldn&apos;t find the page you&apos;re looking for.
        </p>
        <Link href="/">
          <span className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform ">
            Go Home
          </span>
        </Link>
      </div>
      <Footer />
    </>
  );
}
export default Page;
