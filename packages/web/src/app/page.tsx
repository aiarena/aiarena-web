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
        <p>Box: News</p>
        <p> Upcoming tournaments: List</p>
    <p>Top supporters:</p>



        <h1 className="text-4xl font-bold">What is AI Arena?</h1>
        <p className="text-lg mt-4">The AI Arena ladder provides an environment where Scripted and Deep Learning AIs fight in Starcraft 2.

Matches are run 24/7 and streamed to various live-stream platforms. TwtichLink</p>
        <Footer/>
      </div>
    </>
  );
}

export default Page;
