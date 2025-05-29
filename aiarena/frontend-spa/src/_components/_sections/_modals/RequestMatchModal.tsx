import React, { useEffect, useState } from "react";
import Modal from "@/_components/_props/Modal";
import { graphql, useMutation, useQueryLoader } from "react-relay";
import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_props/Form";

import { RequestMatchModalSpecificMapQuery } from "./__generated__/RequestMatchModalSpecificMapQuery.graphql";
import { RequestMatchModalMapPoolQuery } from "./__generated__/RequestMatchModalMapPoolQuery.graphql";
import SelectSearchList from "@/_components/_props/SelectSearchList";
import BotSearchList, {
  BotType,
} from "@/_components/_sections/_modals/BotSearchList.tsx";

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

  //Bot 2 Query
  // ____________________

  const [selectedBot1, setSelectedBot1] = useState<BotType | null>(null);

  // Bot 2 Query
  // ____________________

  const [selectedBot2, setSelectedBot2] = useState<BotType | null>(null);

  //Specific Map Query
  // ____________________
  const [queryVariablesSpecificMap, setQueryVariablesSpecificMap] =
    useState("");

  const [selectedSpecificMap, setSelectedSpecificMap] = useState("");

  const specificMapQuery = graphql`
    query RequestMatchModalSpecificMapQuery($name: String) {
      maps(name: $name, first: 10) {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  `;

  const [specificMapQueryRef, loadSpecificMapQuery] =
    useQueryLoader<RequestMatchModalSpecificMapQuery>(specificMapQuery);
  useEffect(() => {
    loadSpecificMapQuery({ name: queryVariablesSpecificMap });
  }, [queryVariablesSpecificMap, loadSpecificMapQuery]);

  // MapPool Query
  // ____________________
  const [queryVariablesMapPool, setQueryVariablesMapPool] = useState("");

  const [selectedMapPool, setSelectedMapPool] = useState("");

  const mapPoolQuery = graphql`
    query RequestMatchModalMapPoolQuery($name: String) {
      mapPools(name: $name, first: 10) {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  `;
  const [mapPoolQueryRef, loadMapPoolQuery] =
    useQueryLoader<RequestMatchModalMapPoolQuery>(mapPoolQuery);
  useEffect(() => {
    loadMapPoolQuery({ name: queryVariablesMapPool });
  }, [queryVariablesMapPool, loadMapPoolQuery]);
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

    setQueryVariablesSpecificMap("");
    setSelectedSpecificMap("");

    setQueryVariablesMapPool("");
    setSelectedMapPool("");
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
              ? selectedSpecificMap
              : undefined,
          mapPool:
            mapSelectionType === "map_pool" ? selectedMapPool : undefined,
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
  const isFormValid = (): boolean => {
    if (!selectedBot1 || !selectedBot2) {
      return false;
    }
    if (!matchCount || matchCount < 1) {
      return false;
    }

    if (mapSelectionType === "specific_map") {
      if (!selectedSpecificMap) {
        return false;
      }
    } else if (mapSelectionType === "map_pool") {
      if (!selectedMapPool) {
        return false;
      }
    } else {
      return false;
    }

    return true;
  };

  return (
    <Modal onClose={onClose} isOpen={isOpen} title="Request Match">
      <Form
        handleSubmit={handleSubmit}
        submitTitle="Request Match"
        loading={updating}
        disabled={!isFormValid()}
      >
        <div className="mb-4 flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <label className="block text-left font-medium">Bot 1</label>
            <BotSearchList value={selectedBot1} setValue={setSelectedBot1} />
          </div>
          <div className="flex flex-col gap-1">
            <label className="block text-left font-medium">Bot 2</label>
            <BotSearchList value={selectedBot2} setValue={setSelectedBot2} />
          </div>
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
              type="number"
              min="1"
              step="1"
              onChange={(e) => setMatchCount(parseInt(e.target.value))}
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
            <div className="mb-16">
              <label className="block text-left font-medium mb-1">
                Specific Map
              </label>
              {specificMapQueryRef ? (
                <SelectSearchList
                  query={specificMapQuery}
                  dataRef={specificMapQueryRef}
                  dataPath="maps.edges"
                  onChange={(value) => {
                    setQueryVariablesSpecificMap(value);
                  }}
                  onSelect={(value) => {
                    setSelectedSpecificMap(value);
                  }}
                  placeholder="Search for specific map..."
                  maxHeight="small"
                />
              ) : null}
            </div>
          ) : null}
          {mapSelectionType == "map_pool" ? (
            <div className="mb-16">
              <label className="block text-left font-medium mb-1">
                Map pool
              </label>
              {mapPoolQueryRef ? (
                <SelectSearchList
                  query={mapPoolQuery}
                  dataRef={mapPoolQueryRef}
                  dataPath="mapPools.edges"
                  onChange={(value) => {
                    setQueryVariablesMapPool(value);
                  }}
                  onSelect={(value) => {
                    setSelectedMapPool(value);
                  }}
                  placeholder="Search for map pool..."
                  maxHeight="small"
                />
              ) : null}
            </div>
          ) : null}
        </div>
      </Form>
    </Modal>
  );
}
