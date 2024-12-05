"use client";
import Navbar from "@/_components/_nav/Navbar";
import VideoBanner from "@/_components/_display/VideoBanner";
import Footer from "@/_components/_nav/Footer";
import NewsBox from "@/_components/_display/NewsBox";
import PlayerRankingList from "@/_components/_display/PlayerRankingList";
import TopContributorsList from "@/_components/_display/TopContributorList";
import TitleBanner from "@/_components/_examples/TitleBanner";
import React, { useEffect, useState } from "react";
import SmallCompetitionList from "@/_components/_display/SmallCompetitionList";
import { ApiResponse, Competition, News } from "@/types";
import { useLazyLoadQuery } from "react-relay";
import { graphql } from "relay-runtime";

import { useNews } from "@/_components/_hooks/useNews";
import { useCompetitions } from "@/_components/_hooks/useCompetitions";
import { useBots } from "@/_components/_hooks/useBots";
import LatestNews from "@/_components/_display/LatestNews";
import Image from "next/image";
import InitiationHeroTasks from "@/_components/_display/InitiationHeroTasks";
import { ImageOverlayWrapper } from "@/_components/_display/ImageOverlayWrapper";
import DiscordInviteCard from "@/_components/_display/DiscordInviteCard";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";

const tasks = [
  {
    backgroundImage: `/demo_assets/demo_build.webp`,
    title: "Create Your Own Bot",
    description:
      "Create a bot using one of our tutorials. Start developing your own bot today!",
    buttonText: "Create",
    buttonUrl: `${getPublicPrefix()}/create-bot`,
    bgImageAlt: "Alt",
  },
  {
    backgroundImage: `/demo_assets/demo_play.webp`,
    title: "Play Against SC2 Bots",
    description:
      "Play against SC2 bots and test your skills. Discover new strategies to improve your gameplay!",
    buttonText: "Play",
    buttonUrl: `${getPublicPrefix()}/play-bot`,
    bgImageAlt: "Alt",
  },
  {
    backgroundImage: `/demo_assets/demo_compete.webp`,
    title: "Compete On The Ladder",
    description:
      "Compete against other bots on our 24/7 bot ladder. Win achievements and get featured in our tournaments.",
    buttonText: "Competitions",
    buttonUrl: `${getPublicPrefix()}/competitions`,
    bgImageAlt: "Alt",
  },
];

export default function Page() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [news, setNews] = useState<News[]>([]);
  const [error, setError] = useState<string | null>(null);

  const newsData = useNews();

  return (
    <div className="flex flex-col min-h-screen font-sans bg-background-texture">
      <Navbar />
      <main className="flex-grow bg-darken text-white">
        <VideoBanner source={`${getPublicPrefix()}/videos/ai-banner.mp4`}>
          <div className="mt-32 text-6xl font-bold mb-8 font-gugi text-customGreen">
            <Image
              className="mx-auto pb-6 invert h-40 w-40 "
              src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
              alt="AI-arena-logo"
              width={10}
              height={10}
            />
            <h1 className="font-bold font-gugi text-customGreen text-6xl pt-8">
              AI Arena
            </h1>
          </div>
          <h2 className="text-2xl mb-48">
            Welcome to the AI Arena!
          </h2>
          <div className="mb-32">
            <InitiationHeroTasks tasks={tasks} />
          </div>
        </VideoBanner>
        <div className="lg:space-x-4 lg:space-y-0">
          <div className="rounded-lg rounded-lg">
            <ImageOverlayWrapper
              //   imageUrl={`${process.env.PUBLIC_PREFIX}/social_icons/discord-icon.svg`}
              imageUrl={`/generated_assets/dall_e_bg_2.webp`}
              alt="Discord background"
              sectionDivider={true}
              sectionDividerDarken={2}
              blurAmount="blur-md"
              opacityAmount="opacity-70"
            >
              <div className="">
                <div className="min-h-[30em] relative z-10 flex items-center justify-center  ">
                  <DiscordInviteCard
                    serverName="AI Arena"
                    inviteUrl="https://discord.gg/your-invite-code"
                    description="Join the AI Arena discord community"
                    memberCount={2500}
                    onlineCount={450}
                    serverImageUrl={`${getPublicPrefix()}/social_icons/discord-icon.svg`}
                  />
                </div>
              </div>
            </ImageOverlayWrapper>
          </div>
        </div>

        <ImageOverlayWrapper
          imageUrl={`/demo_assets/demo-news.webp`}
          alt="Space Background"
          sectionDivider={true}
          sectionDividerDarken={2}
          blurAmount="blur-sm"
          opacityAmount="opacity-80"
        >
          <LatestNews newsData={newsData} />
        </ImageOverlayWrapper>
      </main>
      <Footer />
    </div>
  );
}
