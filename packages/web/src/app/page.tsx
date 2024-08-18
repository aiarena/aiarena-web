"use client";
import React, { useEffect } from "react";

import Navbar from "@/_components/_nav/Navbar";
// import TestApi from "@/_components/TestApi";
// import { useSession } from "next-auth/react";
function Page() {

  // const { data: session, status } = useSession();
 
  // useEffect(() => {
  //   console.log("session", session, "status", status);
  // }, [session,status]);
  return (
    <>
      <div className="text-center">
        <Navbar />
     
        <h1 className="text-4xl font-bold">Welcome to My Website</h1>
        
        <p className="text-lg mt-4">Here are some standard API calls</p>
        {/* <TestApi /> */}
      </div>
    </>
  );
}

export default Page;
