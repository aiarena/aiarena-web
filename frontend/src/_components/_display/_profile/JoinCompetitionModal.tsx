import React, { useState } from "react";
import Modal from "../Modal";

// import { useCompetitions } from "@/_components/_hooks/useCompetitions";
// import { useToggleCompetitionParticipation } from "@/_components/_hooks/useToggleCompetitionParticipation";
import { getNodes } from "@/_lib/relayHelpers";
import {
  graphql,
  useFragment,
  useLazyLoadQuery,
  useMutation,
} from "react-relay";
import { JoinCompetitionModal_bot$key } from "./__generated__/JoinCompetitionModal_bot.graphql";
import { JoinCompetitionModalCompetitionsQuery } from "./__generated__/JoinCompetitionModalCompetitionsQuery.graphql";
import { JoinCompetitionModalMutation } from "./__generated__/JoinCompetitionModalMutation.graphql";

interface JoinCompetitionModalProps {
  bot: JoinCompetitionModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function JoinCompetitionModal({
  isOpen,
  onClose,
  ...props
}: JoinCompetitionModalProps) {
  const bot = useFragment(
    graphql`
      fragment JoinCompetitionModal_bot on BotType {
        id
        name
        competitionParticipations {
          edges {
            node {
              active
              id
              competition {
                id
                name
                status
              }
            }
          }
        }
      }
    `,
    props.bot
  );
  // TODO
  // maybe theres a better way to fetch this
  const competition_data =
    useLazyLoadQuery<JoinCompetitionModalCompetitionsQuery>(
      graphql`
        query JoinCompetitionModalCompetitionsQuery {
          competitions(last: 20) {
            edges {
              node {
                id
                name
                type
                dateCreated
                status
              }
            }
          }
        }
      `,
      {}
    );

  const [updateCompetitionparticipation] =
    useMutation<JoinCompetitionModalMutation>(graphql`
      mutation JoinCompetitionModalMutation(
        $input: UpdateCompetitionParticipationInput!
      ) {
        updateCompetitionParticipation(input: $input) {
          competitionParticipation {
            active
            id
            bot {
              id
            }
          }
        }
      }
    `);

  const [confirmLeave, setConfirmLeave] = useState<string[]>([]);

  const openCompetitions = getNodes(competition_data.competitions).filter(
    (comp) => comp.status == "OPEN"
  );

  const botCompetitionParticipations = getNodes(bot.competitionParticipations);
  // const [toggleCompetitionParticipation] = useToggleCompetitionParticipation();

  const hasActiveCompetitionParticipation = (competitionId: string) => {
    return (
      botCompetitionParticipations?.some(
        (participation) =>
          competitionId === participation.competition.id &&
          participation.active === true
      ) || false
    );
  };

  // const toggleCompetition = (compId: string) => {
  //   toggleCompetitionParticipation(bot.id, compId, () => {
  //     // Handle the response here
  //   });
  // };

  const handlePromptConfirmLeave = (compId: string) => {
    setConfirmLeave((prev) => [...prev, compId]);
  };

  const handlePromptCancelLeave = (compId: string) => {
    setConfirmLeave((prev) => [...prev].filter((e) => e != compId));
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Edit competitions`}>
      <div className="space-y-4">
        {openCompetitions &&
          openCompetitions.length > 0 &&
          openCompetitions.map((comp) => (
            <div
              className="flex items-center space-x-2 border border-gray-600 rounded-md p-2 justify-between"
              key={comp.id}
            >
              <div className="block">
                <div>
                  <span className="text-gray-300">{comp.name}</span>
                </div>
                <div className="text-left">
                  {hasActiveCompetitionParticipation(comp.id) ? (
                    <span className="text-customGreen">Currently Active</span>
                  ) : (
                    <span className="text-red-400">Currently Inactive</span>
                  )}
                </div>
              </div>
              {hasActiveCompetitionParticipation(comp.id) ? (
                <>
                  {confirmLeave.some((item) => item == comp.id) ? (
                    <div>
                      <button
                        onClick={() => {
                          updateCompetitionparticipation({
                            variables: {
                              input: {
                                competition: comp.id,
                                bot: bot.id,
                                active: false,
                              },
                            },
                          });
                        }}
                        className="bg-red-700 p-2 border  border-gray-600"
                      >
                        Leave
                      </button>
                      <button
                        onClick={() => handlePromptCancelLeave(comp.id)}
                        className="p-2 border  border-gray-600"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handlePromptConfirmLeave(comp.id)}
                      className="bg-red-700 p-2"
                    >
                      Leave
                    </button>
                  )}
                </>
              ) : (
                <button
                  onClick={() => {
                    updateCompetitionparticipation({
                      variables: {
                        input: {
                          competition: comp.id,
                          bot: bot.id,
                          active: true,
                        },
                      },
                    });
                  }}
                  className="bg-customGreen p-2"
                >
                  Join
                </button>
              )}
            </div>
          ))}
      </div>
    </Modal>
  ) : null;
}
