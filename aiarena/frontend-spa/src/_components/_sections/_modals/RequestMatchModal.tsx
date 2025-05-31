import React, { useState } from "react";
import Modal from "@/_components/_props/Modal";
import { graphql, useMutation } from "react-relay";
import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_props/Form";

import BotSearchList, {
  BotType,
} from "@/_components/_sections/_modals/BotSearchList.tsx";
import MapSearchList, {
  MapType,
} from "@/_components/_sections/_modals/MapSearchList.tsx";
import MapPoolSearchList, {
  MapPoolType,
} from "@/_components/_sections/_modals/MapPoolSearchList.tsx";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function RequestMatchModal({ isOpen, onClose }: UploadBotModal) {
  const [mapSelectionType, setMapSelectionType] = useState("specific_map");
  const [matchCount, setMatchCount] = useState(1);
  const [selectedBot1, setSelectedBot1] = useState<BotType | null>(null);
  const [selectedBot2, setSelectedBot2] = useState<BotType | null>(null);
  const [selectedSpecificMap, setSelectedSpecificMap] =
    useState<MapType | null>(null);
  const [selectedMapPool, setSelectedMapPool] = useState<MapPoolType | null>(
    null,
  );

  // Request Match Query
  // ____________________

  const [requestMatch, updating] = useMutation<RequestMatchModalMutation>(
    graphql`
      mutation RequestMatchModalMutation($input: RequestMatchInput!) {
        requestMatch(input: $input) {
          match {
            id
          }
          errors {
            field
            messages
          }
        }
      }
    `,
  );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "requestMatch",
    "Match Requested!",
  );

  const resetAllStateFields = () => {
    setMapSelectionType("specific_map");
    setMatchCount(1);
    setSelectedBot1(null);
    setSelectedBot2(null);
    setSelectedSpecificMap(null);
    setSelectedMapPool(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    requestMatch({
      variables: {
        input: {
          bot1: selectedBot1?.id,
          bot2: selectedBot2?.id,
          matchCount: matchCount,
          mapSelectionType: mapSelectionType,
          chosenMap:
            mapSelectionType === "specific_map"
              ? selectedSpecificMap?.id
              : undefined,
          mapPool:
            mapSelectionType === "map_pool" ? selectedMapPool?.id : undefined,
        },
      },
      onCompleted: (...args) => {
        const success = onCompleted(...args);
        if (success) {
          resetAllStateFields();
          onClose();
        }
      },
      onError,
    });
  };

  return (
    <Modal onClose={onClose} isOpen={isOpen} title="Request Match">
      <Form
        handleSubmit={handleSubmit}
        submitTitle="Request Match"
        loading={updating}
      >
        <div className="mb-4 flex flex-col gap-2">
          <label className="flex flex-col gap-1 font-medium">
            <span>Bot 1</span>
            <BotSearchList value={selectedBot1} setValue={setSelectedBot1} />
          </label>
          <label className="flex flex-col gap-1 font-medium">
            <span>Bot 2</span>
            <BotSearchList value={selectedBot2} setValue={setSelectedBot2} />
          </label>
        </div>
        <div className="mb-4"></div>{" "}
        <div className=" flex flex-wrap gap-4">
          <div className="flex">
            <label className="block text-left font-medium mb-1 pt-2 pr-2">
              Match Count:
            </label>
            <input
              className="w-16"
              value={matchCount}
              onChange={(e) =>
                setMatchCount(parseInt(e.target.value.replace(/\D/g, "")) || 1)
              }
              aria-describedby="match-count-help"
            />
            <div id="match-count-help" className="sr-only">
              Number of games to play between selected bots
            </div>
          </div>
          <div className="block">
            <button
              type="button"
              onClick={() => {
                setMapSelectionType("specific_map");
              }}
              className={` border-2 rounded-lg  bg-darken  ${mapSelectionType == "specific_map" ? "border-customGreen" : "border-gray-700  hover:bg-transparent hover:border-customGreen"} p-2`}
            >
              Specific Map
            </button>{" "}
            <button
              type="button"
              onClick={() => {
                setMapSelectionType("map_pool");
              }}
              className={` border-2  rounded-lg  bg-darken ${mapSelectionType == "map_pool" ? "border-customGreen" : "border-gray-700 hover:bg-transparent hover:border-customGreen"} p-2`}
            >
              Map Pool
            </button>
          </div>
        </div>
        <div>
          {mapSelectionType == "specific_map" ? (
            <label className="mb-16 font-medium flex flex-col gap-1">
              <span>Specific Map</span>
              <MapSearchList
                value={selectedSpecificMap}
                setValue={setSelectedSpecificMap}
              />
            </label>
          ) : null}
          {mapSelectionType == "map_pool" ? (
            <label className="mb-16 font-medium flex flex-col gap-1">
              <span>Map pool</span>
              <MapPoolSearchList
                value={selectedMapPool}
                setValue={setSelectedMapPool}
              />
            </label>
          ) : null}
        </div>
      </Form>
    </Modal>
  );
}
