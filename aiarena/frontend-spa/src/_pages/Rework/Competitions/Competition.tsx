import { graphql, useFragment } from "react-relay";

import type {
  CompetitionCard_competition$data,
  CompetitionCard_competition$key,
} from "./__generated__/CompetitionCard_competition.graphql";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import clsx from "clsx";
import { getIDFromBase64 } from "@/_lib/relayHelpers";

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
        participants {
          totalCount
        }
      }
    `,
    data
  );

  function getGame(competition: CompetitionCard_competition$data) {
    if (competition.game === "StarCraft II") return "starcraft";
    return "generic";
  }
  function getMode(competition: CompetitionCard_competition$data) {
    if (competition.gameMode === "Melee") return "melee";
    if (competition.gameMode === "Micro") return "micro";

    return "melee";
  }
  function getCompetitionImage(competition: CompetitionCard_competition$data) {
    return `${getGame(competition)}_${getMode(competition)}.webp`;
  }

  const imgSrc = `${getPublicPrefix()}/competitions/${getCompetitionImage(competition)}`;

  return (
    <a
      href={`/competitions/${getIDFromBase64(competition.id, "CompetitionType")}`}
      className={clsx(
        "grid md:grid-cols-1 lg:grid-cols-4 rounded-2xl border border-neutral-700 bg-darken-2 backdrop-blur-sm",
        "shadow-lg shadow-black transition-colors hover:border-customGreen"
      )}
    >
      {/* Col 1: Image (small, fixed) */}
      <div id="image" className="col-span-1">
        <img
          src={imgSrc}
          alt={competition.name ?? "Competition Image"}
          className="lg:h-full md:h-[10em] w-full object-cover rounded-t-2xl lg:rounded-tr-none lg:rounded-bl-2xl"
          loading="lazy"
        />
      </div>

      {/* Col 2: Main content (tight, truncates) */}
      <div id="content" className="col-span-2 flex min-w-0 gap-8">
        <div id="competition_metadata" className="w-full pl-4">
          <div>
            <h2 className="font-semibold text-white col-span-1 ">
              {competition.name}
            </h2>
          </div>
          <div className="grid grid-cols-3 mt-3 w-full">
            <div className="col-span-2">
              <div className=" text-gray-300">
                {competition.game && <span>Game: {competition.game}</span>}
              </div>
              <div className=" text-gray-300">
                {competition.gameMode && (
                  <span>Mode: {competition.gameMode}</span>
                )}
              </div>
              <div className=" text-gray-300">
                {competition.gameMode && (
                  <span>
                    Started:{" "}
                    {new Date(competition.dateOpened).toLocaleDateString()}{" "}
                  </span>
                )}
              </div>
            </div>
            <div id="populated_stats" className="text-gray-300">
              <p>
                <span className="text-gray-400">Bots:</span>{" "}
                <span className="text-white">
                  {competition.participants?.totalCount ?? 0}
                </span>
              </p>
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

      {/* Col 4: Leaderboards (tight) */}
      <div id="leaderboards" className="col-span-1"></div>
    </a>
  );
}
