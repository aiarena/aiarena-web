import React, { useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import WrappedTitle from "./WrappedTitle";
import { LegacyCompetitionTop10ListQuery } from "./__generated__/LegacyCompetitionTop10ListQuery.graphql";
import BotIcon from "./BotIcon";
import clsx from "clsx";

import EloTrendIcon from "./EloTrendIcon";
import FetchError from "./FetchError";

const LegacyCompetitonTop10List: React.FC = () => {
  const data = useLazyLoadQuery<LegacyCompetitionTop10ListQuery>(
    graphql`
      query LegacyCompetitionTop10ListQuery {
        competitions(status: OPEN) {
          edges {
            node {
              name
              id
              participants(first: 10) {
                edges {
                  node {
                    bot {
                      id
                      name
                      user {
                        ...BotIcon_user
                      }
                    }
                    trend
                    elo
                    divisionNum
                  }
                }
              }
            }
          }
        }
      }
    `,
    {}
  );
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!data.competitions) {
    return <FetchError type="competitions" />;
  }

  const activeCompetitions = getNodes(data.competitions);

  const handleDotClick = (index: number) => {
    setCurrentIndex(index);
  };

  const competition = activeCompetitions[currentIndex];

  return (
    <div>
      <WrappedTitle title="Competitions" font="font-bold" />
      <div className="text-center mb-4">
        <a
          href={`/competitions/${getIDFromBase64(competition.id, "CompetitionType")}`}
          target="_blank"
          className="font-bold"
        >
          {competition.name}
        </a>
      </div>

      <table className="w-full">
        <thead className="bg-customGreen-dark-2 h-9">
          <tr>
            <th>Rank</th>
            <th></th>
            <th className="text-left">Name</th>
            <th>DIV</th>
            <th>ELO</th>
            <th className="w-12"></th>
          </tr>
        </thead>
        <tbody>
          {getNodes(competition.participants).map((participant, idx) => (
            <tr
              key={participant.bot.id}
              className={clsx(
                "text-sm h-10",
                idx % 2 ? "bg-darken-4" : "bg-darken"
              )}
            >
              <td className="text-center">{idx + 1}</td>
              <td className="m-auto">
                <BotIcon user={participant.bot.user} />
              </td>
              <td>
                <a
                  href={`/bots/${getIDFromBase64(participant.bot.id, "BotType")}`}
                  aria-label={`View bot profile for ${participant.bot.name}`}
                >
                  {participant.bot.name}
                </a>
              </td>
              <td className="text-center">{participant.divisionNum}</td>
              <td className="text-center">{participant.elo}</td>
              <td>
                <EloTrendIcon trend={participant.trend} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex items-center justify-center mt-4">
        {activeCompetitions.map((_, index) => (
          <button
            key={index}
            onClick={() => handleDotClick(index)}
            className={`w-4 h-4 rounded-full mx-1 transition duration-100 ${
              currentIndex === index
                ? "bg-customGreen shadow shadow-black"
                : "bg-gray-400"
            }`}
          ></button>
        ))}
      </div>
    </div>
  );
};

export default LegacyCompetitonTop10List;
