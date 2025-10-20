import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import Modal from "@/_components/_actions/Modal";

import { BotAllParticipationsModal_bot$key } from "./__generated__/BotAllParticipationsModal_bot.graphql";
import { getDateToLocale } from "@/_lib/dateUtils";

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

  return (
    <Modal
      onClose={onClose}
      isOpen={isOpen}
      title={`All Competitions - ${bot.name}`}
    >
      <div className="space-y-4">
        {botCompetitionParticipations &&
          botCompetitionParticipations.length > 0 &&
          botCompetitionParticipations.map((participation) => (
            <div
              className="flex items-center space-x-2 border border-neutral-600 shadow-lg shadow-black rounded-md p-4 justify-between bg-darken-4"
              key={participation.id}
            >
              <div className="block w-full">
                <div className="flex justify-between flex-wrap">
                  <div>
                    <a
                      href={`/competitions/${getIDFromBase64(participation.competition.id, "CompetitionType")}`}
                      className="font-bold"
                    >
                      {participation.competition.name}
                    </a>

                    <dl className="ml-4 text-sm text-gray-300 space-y-2">
                      <div className="flex">
                        <dt className="font-medium text-white w-20 ">
                          Status:
                        </dt>
                        <dd> {participation.competition.status}</dd>
                      </div>
                      <div className="flex">
                        <dt className="font-medium text-white w-20 ">
                          Opened:{" "}
                        </dt>
                        <dd>
                          {getDateToLocale(
                            participation.competition.dateOpened
                          )}
                        </dd>
                      </div>
                      <div className="flex">
                        <dt className="font-medium text-white w-20 ">
                          Closed:{" "}
                        </dt>
                        <dd>
                          {participation.competition.dateClosed != null
                            ? getDateToLocale(
                                participation.competition.dateClosed
                              )
                            : ""}
                        </dd>
                      </div>
                    </dl>
                  </div>

                  <div className="ml-4  pt-4">
                    <dl className=" text-sm text-gray-300 space-y-2">
                      <div className="flex">
                        <dt className="font-medium text-white w-30 ">
                          Division:{" "}
                        </dt>
                        <dd> {participation.divisionNum}</dd>
                      </div>
                      <div className="flex">
                        <dt className="font-medium text-white w-30 ">
                          Win Percentage:{" "}
                        </dt>
                        <dd>{participation.winPerc.toFixed(2)}%</dd>
                      </div>
                    </dl>

                    <a
                      href={`/competitions/stats/${getIDFromBase64(participation.id, "CompetitionParticipationType")}`}
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
  );
}
