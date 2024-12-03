"use client";
import Navbar from "@/_components/_nav/Navbar";
import VideoBanner from "@/_components/_display/VideoBanner";
import Footer from "@/_components/_nav/Footer";
import NewsBox from "@/_components/_display/NewsBox";
import PlayerRankingList from "@/_components/_display/PlayerRankingList";
import TopContributorsList from "@/_components/_display/TopContributorList";
import TitleBanner from "@/_components/_examples/TitleBanner";
import React, {useEffect, useState} from "react";
import SmallCompetitionList from "@/_components/_display/SmallCompetitionList";
import {ApiResponse, Competition, News} from "@/types";
import {useLazyLoadQuery} from "react-relay";
import {graphql} from "relay-runtime";

import {useNews} from "@/_components/_hooks/useNews";
import {useCompetitions} from "@/_components/_hooks/useCompetitions";
import {useBots} from "@/_components/_hooks/useBots";
import LatestNews from "@/_components/_display/LatestNews";


export default function Page() {
    const [competitions, setCompetitions] = useState<Competition[]>([]);
    const [news, setNews] = useState<News[]>([]);
    const [error, setError] = useState<string | null>(null);

    const newsData = useNews();
    // const competitionData = useCompetitions();
    // const botData = useBots()


    return (
        <div className="flex flex-col min-h-screen font-sans">
            <Navbar/>
            <main className="flex-grow bg-darken text-white">
                <VideoBanner source={`${process.env.PUBLIC_PREFIX}/videos/ai-banner.mp4`}/>
                <div className="dividing-line"></div>
                <div className="pt-20 pb-20 px-1">
                    <LatestNews newsData={newsData}/>
                    {/*<div className="flex flex-wrap gap-4 px-4 py-8 justify-around">*/}


                    {/*    <LatestNews newsData={newsData}/>*/}

                    {/*    <div className="flex-grow flex-shrink-0 basis-[300px] min-w-0">*/}
                    {/*        <SmallCompetitionList competitions={botData }/>*/}
                    {/*    </div>*/}
                    {/*</div>*/}
                </div>
            </main>
            <Footer/>
        </div>
    );
}


// "use client";
// import React, { useEffect } from "react";

// import Navbar from "@/_components/_nav/Navbar";
// import VideoComponent from "@/_components/_display/VideoComponent";
// import Footer from "@/_components/_nav/Footer";
// import NewsBox from "@/_components/_display/NewsBox";
// import PlayerRankingList from "@/_components/_display/PlayerRankingList";
// import TopContributorsList from "@/_components/_display/TopContributorList";
// import TitleBanner from "@/_components/_examples/TitleBanner";
// const players = [
//   { rank: 1, race: "Z-icon", name: "Player1", division: 1, elo: 2400 },
//   { rank: 2, race: "P-icon", name: "Player2", division: 1, elo: 2350 },
//   { rank: 3, race: "T-icon", name: "Player3", division: 2, elo: 2300 }
//   // Add more players as needed
// ];

// const contributors = [
//   { name: "Contributor1", amount: 500 },
//   { name: "Contributor2", amount: 300 },
//   { name: "Contributor3", amount: 200 }
//   // Add more contributors as needed
// ];

// function Page() {


//   return (
//     <>
//   <div className="flex flex-col min-h-screen font-sans">
//       <Navbar />

//       <main
//         className="flex-grow bg-fancy-texture text-white"
//         style={{ backgroundImage: `url('${process.env.PUBLIC_PREFIX}/backgrounds/fancy-cushion.png')` }}
//       >

//         <VideoComponent source= {"ai-banner.mp4"}/>

//         <div className="pt-20">
//         <TitleBanner title="Some buttons" />
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 px-4 py-8">

//           <div className="w-full">
//             <NewsBox
//               title="Exciting Update nr 12385"
//               date="August 18, 2024"
//               content="Here are the latest updates from the community."
//               videoUrl="news-video.mp4"
//             />
//           </div>

//           <div className="w-full">
//             <PlayerRankingList players={players} />
//           </div>
//           <div className="w-full">
//             <TopContributorsList contributors={contributors} />
//           </div>
//         </div>
//         </div>


//       </main>

//       <Footer />
//     </div>
//     </>
//   );
// }

// export default Page;
