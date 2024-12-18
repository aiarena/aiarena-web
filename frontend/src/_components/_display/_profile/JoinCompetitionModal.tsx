import React, { useState } from "react";
import Modal from "../Modal";
import { Bot } from "../ProfileBotOverviewList";
// import Modal from "../Modal";

interface Competition {
  name: string;
}

interface JoinCompetitionModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
  competitions: Competition[]
}


export default function JoinCompetitionModal({ bot, competitions, isOpen, onClose }: JoinCompetitionModalProps) {
  const [selectedCompetitions, setSelectedCompetitions] = useState<string[]>([]);

  // const toggleCompetition = (competition) => {
  //   setSelectedCompetitions((prev) =>
  //     prev.includes(competition)
  //       ? prev.filter((c) => c !== competition)
  //       : [...prev, competition]
  //   );
  // };
  console.log("init modal")
  const handleJoin = () => {
    console.log("Joining Competitions", selectedCompetitions);
    onClose();
  };


  return isOpen ? (
    <Modal onClose={onClose} title="Competitions">
      <div className="space-y-4">
        <h4 className="text-lg text-gray-300">Available Competitions</h4>
        {bot.activeCompetitions.map((comp, index) => (
          <div key={index} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedCompetitions.includes(comp.name)}
              // onChange={() => toggleCompetition(comp.name)}
              className="form-checkbox"
            />
            <span className="text-gray-300">{comp.name}</span>
          </div>
        ))}
        <button
          onClick={handleJoin}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Join Competition
        </button>
      </div>
    </Modal>
  ) : null;
}
