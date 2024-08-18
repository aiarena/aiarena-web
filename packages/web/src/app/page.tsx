"use client";
import React, { useEffect } from "react";

import Navbar from "@/_components/_nav/Navbar";
import VideoComponent from "@/_components/_display/VideoComponent";
import Footer from "@/_components/_nav/Footer";
import NewsBox from "@/_components/_display/NewsBox";
import PlayerRankingList from "@/_components/_display/PlayerRankingList";
import TopContributorsList from "@/_components/_display/TopContributorList";
const players = [
  { rank: 1, race: "Z-icon", name: "Player1", division: 1, elo: 2400 },
  { rank: 2, race: "P-icon", name: "Player2", division: 1, elo: 2350 },
  { rank: 3, race: "T-icon", name: "Player3", division: 2, elo: 2300 }
  // Add more players as needed
];

const contributors = [
  { name: "Contributor1", amount: 500 },
  { name: "Contributor2", amount: 300 },
  { name: "Contributor3", amount: 200 }
  // Add more contributors as needed
];

function Page() {

  return (
    <>
      <div>
        <Navbar />
        <VideoComponent source= {"ai-banner.mp4"}/>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 px-4 py-8">
          <div className="w-full">
            <NewsBox
              title="Exciting Updates"
              date="August 18, 2024"
              content="Here are the latest updates from the community."
              videoUrl="news-video.mp4"
            />
          </div>
          <div className="w-full">
            <PlayerRankingList players={players} />
          </div>
          <div className="w-full">
            <TopContributorsList contributors={contributors} />
          </div>
        </div>


        <Footer/>
      </div>
    </>
  );
}

export default Page;
