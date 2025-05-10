import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import Modal from "@/_components/_props/Modal";

import { BotAllParticipationsModal_bot$key } from "./__generated__/BotAllParticipationsModal_bot.graphql";
import { formatDate } from "@/_lib/dateUtils";

interface BotAllParticipationsModalProps {
  bot: BotAllParticipationsModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function BotAllParticipationsModal({
  isOpen,
  onClose,
  ...props
}: BotAllParticipationsModalProps) {
  const bot = useFragment(
    graphql`
      fragment BotAllParticipationsModal_bot on BotType {
        id
        name
        competitionParticipations {
          edges {
            node {
              active
              id
              divisionNum
              winPerc

              competition {
                id
                name
                status
                dateOpened
                dateClosed
              }
            }
          }
        }
      }
    `,
    props.bot
  );

  const botCompetitionParticipations = getNodes(bot.competitionParticipations);

  return isOpen ? (
    <Modal onClose={onClose} title={`All Competitions - ${bot.name}`}>
      <div className="space-y-4">
        {botCompetitionParticipations &&
          botCompetitionParticipations.length > 0 &&
          botCompetitionParticipations.map((participation) => (
            <div
              className="flex items-center space-x-2 border border-gray-600 rounded-md p-2 justify-between"
              key={participation.id}
            >
              <div className="block w-full">
                <div className="flex justify-between">
                  <div>
                    <a
                      href={`/competitions/${extractRelayID(participation.competition.id, "CompetitionType")}`}
                      className="text-sm font-semibold"
                    >
                      {participation.competition.name}
                    </a>
                    <p>
                      Opened: {formatDate(participation.competition.dateOpened)}
                    </p>
                    <p>
                      Closed:
                      {participation.competition.dateClosed != null
                        ? formatDate(participation.competition.dateClosed)
                        : ""}
                    </p>
                    <p> Status: {participation.competition.status}</p>
                  </div>

                  <div className="pr-2">
                    <p> Division: {participation.divisionNum}</p>

                    <p> Win Percentage: {participation.winPerc.toFixed(2)}%</p>
                    <a
                      href={`/competitions/stats/${extractRelayID(participation.id, "CompetitionParticipationType")}`}
                    >
                      Explore more stats
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    </Modal>
  ) : null;
}
