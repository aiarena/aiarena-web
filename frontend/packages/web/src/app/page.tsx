"use client";
import Navbar from "@/_components/_nav/Navbar";
import VideoBanner from "@/_components/_display/VideoBanner";
import Footer from "@/_components/_nav/Footer";
import NewsBox from "@/_components/_display/NewsBox";
import PlayerRankingList from "@/_components/_display/PlayerRankingList";
import TopContributorsList from "@/_components/_display/TopContributorList";
import TitleBanner from "@/_components/_examples/TitleBanner";
import { useEffect, useState } from "react";
import SmallCompetitionList from "@/_components/_display/SmallCompetitionList";
import { ApiResponse, Competition, News } from "@/types"; // Ensure this path is correct

export default function Page() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [news, setNews] = useState<News[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/proxy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: `
            {
              competitions(status: OPEN) {
                edges {
                  node {
                    name
                    participants(first: 10) {
                      edges {
                        node {
                          bot {
                            name
                          }
                          elo
                          trend
                          divisionNum
                        }
                      }
                    }
                  }
                }
              }
              news {
                edges {
                  node {
                    title
                    ytLink
                    created
                  }
                }
              }
            }
          `,
          }),
        });

        const result: { data: ApiResponse } = await response.json();
        console.log(result);

        if (result.data) {
          setCompetitions(result.data.competitions.edges);
          setNews(result.data.news.edges);
        } else {
          throw new Error('No data found');
        }
      } catch (error) {
        if (error instanceof Error) {
          // If the error is an instance of Error, you can safely access its message
          setError(error.message);
        } else {
          // Handle the case where error is not an instance of Error (unlikely, but possible)
          setError('An unexpected error occurred');
        }
      }
    }

    fetchData();
  }, []);

  return (
    <div className="flex flex-col min-h-screen font-sans bg-background-texture">
      <Navbar />
      <main className="flex-grow bg-darken text-white">
        <VideoBanner source="./videos/ai-banner.mp4" />
        <div className="dividing-line"></div>
        <div className="pt-20">
          {/* <TitleBanner title="Some buttons" /> */}
          {/* <div className="dividing-line"></div> */}
          <br/>
          <br/>
        

          <div className="flex flex-wrap gap-4 px-4 py-8">
  {news.length > 0 && (
    <div className="flex-grow flex-shrink-0 basis-[300px] min-w-0">
      <NewsBox
        title={news[0].node.title}
        date={new Date(news[0].node.created).toLocaleDateString()}
        content="Latest updates from the community."
        videoUrl={news[0].node.ytLink}
      />
    </div>
  )}
  <div className="flex-grow flex-shrink-0 basis-[300px] min-w-0">
    <SmallCompetitionList competitions={competitions} />
  </div>
</div>
        </div>
      </main>
      <Footer />
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
      
//       <main className="flex-grow bg-fancy-texture text-white">
       
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
