import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import { BotParticipationCard_bot$key } from "./__generated__/BotParticipationCard_bot.graphql";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import AiArenaLoading from "@/_components/_display/AiArenaLoading";

interface BotParticipationCardProps {
  data: BotParticipationCard_bot$key;
}

export default function BotParticipationCard(props: BotParticipationCardProps) {
  const data = useFragment(
    graphql`
      fragment BotParticipationCard_bot on CompetitionParticipationType {
        id
        bot {
          id
          name
        }
        competition {
          id
          name
        }
        divisionNum
        elo
        winPerc
      }
    `,
    props.data,
  );

  const competitionLink = `/competitions/${getIDFromBase64(data.competition.id, "CompetitionType")}`;

  return (
    <div className="grid grid-cols-5 rounded-2xl border border-neutral-800 bg-darken-2 backdrop-blur-sm p-1 mr-2 shadow-lg bg-blur-2xl">
      <span className="p-3">
        <AiArenaLoading text={""} size={50} speedMs={15000} />
      </span>
      <div className="col-span-4">
        <p className="truncate ">
          <Link to={competitionLink}>{data.competition.name}</Link>
        </p>
        <div className="flex flex-wrap gap-4">
          <div>
            <div className="flex gap-1 ">
              <dt className=" text-gray-400">Division: </dt>
              <dd className="flex-1 text-gray-100"> {data.divisionNum} </dd>
            </div>
            <div className="flex gap-1">
              <dt className=" text-gray-400">Elo: </dt>
              <dd className="flex-1 text-gray-100"> {data.elo} </dd>
            </div>
          </div>
          <div>
            <div className="flex gap-1">
              <dt className=" text-gray-400">Win: </dt>
              <dd className="flex-1 text-gray-100">
                {Math.trunc(data.winPerc)}%
              </dd>
            </div>
            <a
              href={`/competitions/stats/${getIDFromBase64(data.id, "CompetitionParticipationType")}`}
            >
              View Stats
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
