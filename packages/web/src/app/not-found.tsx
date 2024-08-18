"use client";
import React, { useEffect } from "react";
import Layout from "./(unprotected_pages)/layout";
import Navbar from "@/_components/_nav/Navbar";
import { useSession } from "next-auth/react";

function Page() {
  const { data: session, status } = useSession();
  console.log(session);
  useEffect(() => {
    console.log(session);
  }, [session]);

  return (
    <>
      <Navbar />
      <div className="text-center">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="text-lg mt-4">Page was not found.</p>
      </div>
    </>
  );
}
export default Page;
