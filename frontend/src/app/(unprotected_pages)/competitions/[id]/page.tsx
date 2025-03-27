"use client";
import CompetitionHeader from "@/_components/_display/CompetitionHeader";
import VideoPlayer from "@/_components/_display/VideoPlayer";
import { getFeatureFlags } from "@/_data/featureFlags";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import ToggleCompetitionDataDisplay from "@/_components/_display/ToggleCompetitionDataDisplay";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageCompetitionQuery } from "./__generated__/pageCompetitionQuery.graphql";
import MapImagesCompetitionDisplay from "@/_components/_display/CompetitionMapsDisplay";
import LoadingDots from "@/_components/_display/LoadingDots";

interface CompetitionPageProps {
  params: {
    id: string;
  };
}

export default function Page(props: CompetitionPageProps) {
  const competition = useLazyLoadQuery<pageCompetitionQuery>(
    graphql`
      query pageCompetitionQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
            id
            dateClosed
            dateCreated
            dateOpened
            ...CompetitionHeader_competition
            ...CompetitionMapsDisplay_competition
          }
        }
      }
    `,
    { id: decodeURIComponent(props.params.id) }
  );

  const featureFlags = getFeatureFlags();

  if (!competition.node) {
    notFound();
  }

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <CompetitionHeader competition={competition.node} />

      {/* Main Content Section */}
      <div className=" px-4 sm:px-6 lg:px-8 max-w-9xl mx-auto space-y-6">
        {/* Competition Details and About Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Basic Info */}
          <div className="border-gray-800 border-2 bg-customBackgroundColor1D1 p-6 rounded-lg shadow-md">
            <h3 className=" text-2xl font-semibold text-customGreen mb-4">
              Competition Details
            </h3>
            <div className="space-y-2 text-white">
              {/* You can add more details here if needed */}
            </div>

            <p className="text-white leading-relaxed">
              The SC2 AI Arena 2024 Season 2 competition is the ultimate proving
              ground for bots, featuring the main SC2 AI ladder with all
              official maps and standard melee rules. It rigorously tests
              strategy, micro, resource management, and decision-making.
            </p>
          </div>
          {featureFlags.competitionMaps && !featureFlags.competitionVideo ? (
            <div className="border-gray-700 border-2 bg-customBackgroundColor1  rounded-lg shadow-md lg:col-span-2">
              <MapImagesCompetitionDisplay competition={competition.node} />
            </div>
          ) : null}

          {featureFlags.competitionVideo ? (
            <div className="border-gray-700 border-2 bg-customBackgroundColor1  p-6 rounded-lg shadow-md lg:col-span-2">
              <h2 className="text-3xl font-bold text-customGreen mb-4">
                Live Stream
              </h2>
              <div className="relative ">
                <VideoPlayer
                  src="/videos/ai-banner.mp4" // Local or hosted video file
                  poster="/images/video-poster.jpg" // Optional poster image
                  alt="Sample video demonstrating the AI competition."
                  controls={true}
                  autoPlay={true}
                  loop={true}
                  muted={true}
                />
              </div>
            </div>
          ) : null}
        </div>

        {/* Client-side rendered participations with Suspense boundary */}
        <Suspense
          fallback={
            <div className="pt-12 pb-24 items-center">
              <p>Loading rounds and competition rankings...</p>
              <LoadingDots className={"pt-2"} />
            </div>
          }
        >
          {competition.node.id && (
            <ToggleCompetitionDataDisplay competitionId={competition.node.id} />
          )}
        </Suspense>
      </div>
    </div>
  );
}
