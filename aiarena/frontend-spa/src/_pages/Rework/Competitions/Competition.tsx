import { graphql, useFragment } from "react-relay";

import type {
  // CompetitionCard_competition$data,
  CompetitionCard_competition$key,
} from "./__generated__/CompetitionCard_competition.graphql";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import clsx from "clsx";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import CompetitionParticipantCount from "@/_components/_display/CompetitionParticipantCount";
import { Suspense } from "react";
import LoadingDots from "@/_components/_display/LoadingDots";

interface CompetitionCardProps {
  data: CompetitionCard_competition$key;
}

export default function CompetitionCard({ data }: CompetitionCardProps) {
  const competition = useFragment(
    graphql`
      fragment CompetitionCard_competition on CompetitionType {
        id
        name
        dateClosed
        dateOpened
        status
        game
        gameMode

        rounds {
          totalCount
        }
      }
    `,
    data
  );

  // function getGame(competition: CompetitionCard_competition$data) {
  //   if (competition.game === "StarCraft II") return "starcraft";
  //   return "starcraft";
  // }
  // function getMode(competition: CompetitionCard_competition$data) {
  //   if (competition.gameMode === "Melee") return "melee";
  //   if (competition.gameMode === "Micro") return "micro";

  //   return "melee";
  // }
  // function getCompetitionImage(competition: CompetitionCard_competition$data) {
  //   return `${getGame(competition)}_${getMode(competition)}.webp`;
  // }

  // const imgSrc = `${getPublicPrefix()}/competitions/${getCompetitionImage(competition)}`;

  function GenerateCompetitionImage() {
    return (
      <span className="w-full text-white flex flex-col items-center justify-center h-full text-center">
        <img
          className="invert"
          src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
          alt="AI-arena-logo"
          width={128}
          height={48}
        />
      </span>
    );
  }

  return (
    <a
      href={`/competitions/${getIDFromBase64(competition.id, "CompetitionType")}`}
      className={clsx(
        "p-2  grid grid-cols-1 lg:grid-cols-4 rounded-2xl border border-neutral-800 bg-darken-2 backdrop-blur-sm",
        "shadow-lg shadow-black transition hover:scale-102  duration-100  "
      )}
    >
      <div id="image" className="col-span-1 m-4 lg:p-0 md:p-8 p-2">
        <GenerateCompetitionImage />
      </div>

      <div id="content" className="col-span-2 flex min-w-0 gap-8">
        <div id="competition_metadata" className="w-full pl-4">
          <div>
            <h2 className="font-semibold text-white col-span-1 ">
              {competition.name}
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 grid-cols-1 my-3 w-full">
            <div id="populated_stats" className="text-gray-300 ml-2">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Game:</span>{" "}
                <span className="text-white">{competition.game}</span>
              </div>
              <p>
                <span className="text-gray-400">Mode:</span>{" "}
                <span className="text-white">{competition.gameMode}</span>
              </p>
              <p>
                <span className="text-gray-400">Started:</span>{" "}
                <span className="text-white">
                  {new Date(competition.dateOpened).toLocaleDateString()}
                </span>
              </p>
            </div>

            <div id="populated_stats" className="text-gray-300 ml-2">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Bots:</span>
                <Suspense fallback={<LoadingDots />}>
                  <CompetitionParticipantCount competitionId={competition.id} />
                </Suspense>
              </div>
              <p>
                <span className="text-gray-400">Round:</span>{" "}
                <span className="text-white">
                  {competition.rounds?.totalCount ?? 0}
                </span>
              </p>
              <p>
                <span className="text-gray-400">Status:</span>{" "}
                <span className="text-white">{competition.status ?? 0}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Col 4 reserved for new feature */}
      <div id="leaderboards" className="col-span-1"></div>
    </a>
  );
}
