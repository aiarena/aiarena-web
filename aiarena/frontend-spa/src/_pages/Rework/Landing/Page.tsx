import LatestNews from "@/_components/_display/LatestNews";
import LegacyActivityList from "@/_components/_display/LegacyActivityList";
import LegacyCompetitonTop10List from "@/_components/_display/LegacyCompetitionTop10List";
import LegacyStats from "@/_components/_display/LegacyStats";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { ClipboardDocumentListIcon } from "@heroicons/react/16/solid";

import { ReactNode, Suspense } from "react";

import "react-loading-skeleton/dist/skeleton.css";
import DisplaySkeletonBlockWithTitle from "@/_components/_display/_skeletons/DisplaySkeletonBlockWithTitle";

export default function LandingPage() {
  return (
    <div className="bg-linear-[90deg,rgba(0,0,0,0)_5%,rgba(0,0,0,0.3)_50%,rgba(0,0,0,0)_90%]">
      <div className="relative z-10 pb-10 md:pt-0 pt-20">
        <Hero />
        <CapWidth>
          <div className="md:w-full md:grid m-auto grid-cols-2 gap-40">
            <div className="col-span-1">
              <CardsAndNewsSection />
            </div>
            <div className="col-span-1">
              <CompetitionsAndActivity />
            </div>
          </div>
        </CapWidth>
      </div>
    </div>
  );
}

function CardsAndNewsSection() {
  return (
    <>
      <div className="float-half-left grid gap-8">
        <div>
          <WrappedTitle title="What is AI Arena?" font="font-bold" />
          <div id="whatisaiarena">
            The AI Arena ladder provides an environment where Scripted and Deep
            Learning AIs fight in Starcraft 2.
            <br />
            <br />
            Matches are run 24/7 and <a href="/stream/">streamed</a> to various
            live-stream platforms.
          </div>
        </div>
        <div>
          {" "}
          <WrappedTitle title="Problems?" font="font-bold" />
          <div id="problems">
            Any problems with the website can be reported in our
            <a href="https://discord.gg/Emm5Ztz"> Discord</a>.
          </div>
        </div>
        <div>
          <WrappedTitle title="Want to help out?" font="font-bold" />
          <div id="contribute">
            Refer to the <a href="https://aiarena.net/wiki/contribute/">wiki</a>{" "}
            on ways to contribute.
          </div>
        </div>
        <Suspense fallback={<DisplaySkeletonBlockWithTitle bodyHeight={410} />}>
          <LatestNews />
        </Suspense>
        <Suspense fallback={<DisplaySkeletonBlockWithTitle bodyHeight={200} />}>
          <LegacyStats />
        </Suspense>
      </div>
    </>
  );
}

function CompetitionsAndActivity() {
  return (
    <>
      <div className="float-half-left grid gap-8">
        <Suspense
          fallback={
            <div>
              <DisplaySkeletonBlockWithTitle bodyHeight={500} />
              <div className="py-6"></div>
              <DisplaySkeletonBlockWithTitle bodyHeight={610} />
            </div>
          }
        >
          <LegacyCompetitonTop10List />
          <LegacyActivityList />
        </Suspense>
      </div>
    </>
  );
}

function Hero() {
  return (
    <div className="min-h-[50vh] flex items-center justify-center mb-8">
      <div>
        <div>
          <img
            className="invert m-auto mb-8"
            src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
            alt="AI-arena-logo"
            height={120}
            width={120}
          />
          <h1 className="text-center pb-4 text-5xl font-gugi font-thin text-customGreen">
            AI Arena
          </h1>
          <WrappedTitle title="Welcome to the Arena" font="font-bold" />
        </div>
        <div className="flex justify-center gap-4">
          <InstructionsCard />
        </div>
      </div>
    </div>
  );
}

function InstructionsCard() {
  return (
    <>
      <div className="border-2 border-customGreen p-4 rounded-md bg-darken-2 grid gap-4">
        <h3 className="flex gap-4">
          <ClipboardDocumentListIcon width={20} /> Instructions
        </h3>
        <ol className="list-decimal ml-10">
          <li>
            <a href="/accounts/register/" target="_blank">
              Register
            </a>
          </li>
          <li>
            Read the{" "}
            <a
              href="https://aiarena.net/wiki/bot-development/getting-started/"
              target="_blank"
            >
              Getting Started
            </a>{" "}
            guide
          </li>
          <li>Upload your Bot to the Website and activate it</li>
        </ol>
        <p>
          Your Bot will be added to the pool and starts fighting other Bots on
          the Ladder.
        </p>
      </div>
    </>
  );
}

function CapWidth({ children }: { children: ReactNode }) {
  return (
    <>
      <div className="max-w-[60em] m-auto">{children}</div>
    </>
  );
}
