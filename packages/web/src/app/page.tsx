"use client";
import React, { useEffect } from "react";

import Navbar from "@/_components/_nav/Navbar";
import VideoComponent from "@/_components/_display/VideoComponent";
import Footer from "@/_components/_nav/Footer";

function Page() {

  return (
    <>
      <div>
        <Navbar />
        <VideoComponent source= {"ai-banner.mp4"}/>
        <h1 className="text-4xl font-bold">Welcome to My Website</h1>
        <p className="text-lg mt-4">Here are some standard API calls</p>
        <Footer/>
      </div>
    </>
  );
}

export default Page;
