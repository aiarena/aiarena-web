"use client";
import React from "react";
import Navbar from "@/_components/_nav/Navbar";
import Footer from "@/_components/_nav/Footer";
import Link from "next/link";

function Page() {
  return (
    <>
      <div className="flex flex-col min-h-screen ">
        <Navbar />
        <div className="flex flex-col items-center justify-center flex-grow text-center relative min-h-[60em]  bg-darken">
          <h1 className="text-9xl font-extrabold tracking-widest relative">
            404
            <span className="bg-customGreen px-3 py-1 text-sm font-semibold tracking-normal rounded rotate-6 absolute top-16 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
              Page Not Found
            </span>
          </h1>
          <p className="text-lg mt-12 mb-10">
            Sorry, we couldn&apos;t find the page you&apos;re looking for.
          </p>
          <Link href="/">
            <span className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform">
              Back to Home
            </span>
          </Link>
        </div>
        <Footer />
      </div>
    </>
  );
}
export default Page;
