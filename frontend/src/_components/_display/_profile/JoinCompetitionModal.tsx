import React, { useState } from "react";
import Modal from "../Modal";
import { Bot } from "../ProfileBotOverviewList";
import { useCompetitions } from "@/_components/_hooks/useCompetitions";
import { PassThrough } from "stream";
import { useToggleCompetitionParticipation } from "@/_components/_hooks/useToggleCompetitionParticipation";
// import Modal from "../Modal";

// interface Competition {
//   name: string;
// }

interface JoinCompetitionModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
  // competitions: Competition[]
}

export default function JoinCompetitionModal({
  bot,
  isOpen,
  onClose,
}: JoinCompetitionModalProps) {
  const [selectedCompetitions, setSelectedCompetitions] = useState<string[]>(
    []
  );

  const [confirmLeave, setConfirmLeave] = useState<string[]>([]);
  const competitions = useCompetitions();

  const openCompetitions = competitions.filter((comp) => comp.status == "OPEN");

  const botCompetitionParticipations = bot.competitionParticipations;
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

  console.log(openCompetitions);

  const toggleCompetition = (compId: string) => {
    toggleCompetitionParticipation(bot.id, compId, (response) => {
      // Handle the response here
      console.log("response", response);
    });
  };

  const handlePromptConfirmLeave = (compId: string) => {
    setConfirmLeave((prev) => [...prev, compId]);
    console.log(confirmLeave)
  };

  const handlePromptCancelLeave = (compId: string) => {
    setConfirmLeave((prev) => [...prev].filter((e) => e != compId));
    console.log(confirmLeave)
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
                      <button onClick={() => toggleCompetition(comp.id)} className="bg-red-700 p-2 border  border-gray-600">Leave</button>
                      <button onClick={() => handlePromptCancelLeave(comp.id)} className="p-2 border  border-gray-600" >Cancel</button>
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
