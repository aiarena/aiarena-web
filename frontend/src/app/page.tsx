import Navbar from "@/_components/_nav/Navbar";
import VideoBanner from "@/_components/_display/VideoBanner";
import Footer from "@/_components/_nav/Footer";
import React from "react";
import LatestNews from "@/_components/_display/LatestNews";
import Image from "next/image";
import InitiationHeroTasks from "@/_components/_display/InitiationHeroTasks";
import { ImageOverlayWrapper } from "@/_components/_display/ImageOverlayWrapper";
import DiscordInviteCard from "@/_components/_display/DiscordInviteCard";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { getFeatureFlags } from "@/_data/featureFlags";
import MainButton from "@/_components/_props/MainButton";
import { fetchQuery, graphql } from "relay-runtime";
import { initEnvironment } from "@/_lib/relay/RelayEnvironment";
import { pageNewsQuery } from "./__generated__/pageNewsQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";

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
      "Compete against other bots in the arena. Win achievements and get featured in our tournaments.",
    buttonText: "Competitions",
    buttonUrl: `${getPublicPrefix()}/competitions`,
    bgImageAlt: "Alt",
  },
];

const NewsQuery = graphql`
  query pageNewsQuery {
    news(last: 5) {
      edges {
        node {
          id
          title
          text
          created
          ytLink
        }
      }
    }
  }
`;

// This is a working server side fetch implementation, note async await in page and fetchNewsData function

async function fetchNewsData() {
  const environment = initEnvironment();
  try {
    const newsData = await fetchQuery<pageNewsQuery>(
      environment,
      NewsQuery,
      {}
    ).toPromise();

    return newsData;
  } catch (error) {
    console.error("Error fetching news data:", error);
  }
}

export default async function Page() {
  const heroTasks = getFeatureFlags().heroTasks;

  const newsData = await fetchNewsData();

  return (
    <>
      <div className="flex flex-col min-h-screen font-sans bg-background-texture">
        <Navbar />

        <main className="flex-grow bg-darken text-white">
          <VideoBanner source={`${getPublicPrefix()}/videos/ai-banner.mp4`}>
            <div className="text-6xl font-bold font-gugi text-customGreen">
              <Image
                className="m-auto pb-6 invert h-40 w-40 "
                src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
                alt="AI-arena-logo"
                width={10}
                height={10}
              />
              <h1 className="font-bold font-gugi text-customGreen text-6xl pt-8">
                AI Arena
              </h1>
            </div>
            <h2 className="text-2xl mb-12">Welcome to the AI Arena!</h2>
            {heroTasks ? (
              <div className="mb-32 mt-36">
                <InitiationHeroTasks tasks={tasks} />
              </div>
            ) : (
              <MainButton href={`${getPublicPrefix()}/login/`} text="Login" />
            )}
          </VideoBanner>
          <div className="lg:space-x-4 lg:space-y-0">
            <div className="rounded-lg rounded-lg">
              <ImageOverlayWrapper
                imageUrl={`/generated_assets/dall_e_bg_2.webp`}
                alt="Discord background"
                sectionDivider={true}
                sectionDividerDarken={5}
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
          {newsData ? (
            <ImageOverlayWrapper
              imageUrl={`/demo_assets/demo-news.webp`}
              alt="Space Background"
              sectionDivider={true}
              sectionDividerDarken={5}
              blurAmount="blur-sm"
              opacityAmount="opacity-80"
            >
              <LatestNews newsData={getNodes(newsData.news)} />
            </ImageOverlayWrapper>
          ) : null}
        </main>
        <Footer />
      </div>
    </>
  );
}
