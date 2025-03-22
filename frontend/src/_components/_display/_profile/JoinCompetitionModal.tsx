import React, { useState } from "react";
import Modal from "../Modal";

import { useCompetitions } from "@/_components/_hooks/useCompetitions";
import { PassThrough } from "stream";
import { useToggleCompetitionParticipation } from "@/_components/_hooks/useToggleCompetitionParticipation";
import { getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import { JoinCompetitionModal_bot$key } from "./__generated__/JoinCompetitionModal_bot.graphql";


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

  const [confirmLeave, setConfirmLeave] = useState<string[]>([]);
  const competitions = useCompetitions();

  const openCompetitions = competitions.filter((comp) => comp.status == "OPEN");

  const botCompetitionParticipations = getNodes(bot.competitionParticipations);
  const [toggleCompetitionParticipation, isInFlight, error] =
    useToggleCompetitionParticipation();

  const hasActiveCompetitionParticipation = (competitionId: string) => {
    return (
      botCompetitionParticipations?.some(
        (participation) =>
          competitionId === participation.competition.id &&
          participation.active === true
      ) || false
    );
  };

  const toggleCompetition = (compId: string) => {
    toggleCompetitionParticipation(bot.id, compId, (response) => {
      // Handle the response here
    });
  };

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
          openCompetitions.map((comp, index) => (
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
                        onClick={() => toggleCompetition(comp.id)}
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
                  onClick={() => toggleCompetition(comp.id)}
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
