import React, { useEffect, useState } from "react";
import Modal from "@/_components/_props/Modal";
import { graphql, useMutation, useQueryLoader } from "react-relay";

import { RequestMatchModalBot1Query } from "./__generated__/RequestMatchModalBot1Query.graphql";

import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_props/Form";
import SelectSearchListV2 from "@/_components/_props/SelectSearchListv2";
import { RequestMatchModalBot2Query } from "./__generated__/RequestMatchModalBot2Query.graphql";
import { RequestMatchModalSpecificMapQuery } from "./__generated__/RequestMatchModalSpecificMapQuery.graphql";
import { RequestMatchModalMapPoolQuery } from "./__generated__/RequestMatchModalMapPoolQuery.graphql";

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

  const [queryVariablesBot1Refactor, setQueryVariablesBot1Refactor] =
    useState("");
  const [selectedBot1Refactor, setSelectedBot1Refactor] = useState("");

  const [queryVariablesBot2Refactor, setQueryVariablesBot2Refactor] =
    useState("");
  const [selectedBot2Refactor, setSelectedBot2Refactor] = useState("");

  const [
    queryVariablesSpecificMapRefactor,
    setQueryVariablesSpecificMapRefactor,
  ] = useState("");

  const [selectedSpecificMapRefactor, setSelectedSpecificMapRefactor] =
    useState("");

  const [queryVariablesMapPoolRefactor, setQueryVariablesMapPoolRefactor] =
    useState("");

  const [selectedMapPoolRefactor, setSelectedMapPoolRefactor] = useState("");

  const bot1Query = graphql`
    query RequestMatchModalBot1Query($name: String) {
      bots(name: $name, first: 10) {
        edges {
          node {
            id
            name
            created
            botZipUpdated
            user {
              id
              username
            }
          }
        }
      }
    }
  `;

  const [bot1QueryRef, loadBot1Query] =
    useQueryLoader<RequestMatchModalBot1Query>(bot1Query);

  useEffect(() => {
    loadBot1Query({ name: queryVariablesBot1Refactor });
  }, [queryVariablesBot1Refactor, loadBot1Query]);

  const bot2Query = graphql`
    query RequestMatchModalBot2Query($name: String) {
      bots(name: $name, first: 10) {
        edges {
          node {
            id
            name
            created
            botZipUpdated
            user {
              id
              username
            }
          }
        }
      }
    }
  `;

  const [bot2QueryRef, loadBot2Query] =
    useQueryLoader<RequestMatchModalBot2Query>(bot2Query);
  useEffect(() => {
    loadBot2Query({ name: queryVariablesBot2Refactor });
  }, [queryVariablesBot2Refactor, loadBot2Query]);

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
    loadSpecificMapQuery({ name: queryVariablesSpecificMapRefactor });
  }, [queryVariablesSpecificMapRefactor, loadSpecificMapQuery]);

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
    loadMapPoolQuery({ name: queryVariablesMapPoolRefactor });
  }, [queryVariablesMapPoolRefactor, loadMapPoolQuery]);

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
    `
  );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "requestMatch",
    "Match Request Updated!"
  );

  const resetAllStateFields = () => {
    setMapSelectionType("specific_map");
    setMatchCount(1);

    setQueryVariablesBot1Refactor("");
    setSelectedBot1Refactor("");

    setQueryVariablesBot2Refactor("");
    setSelectedBot2Refactor("");

    setQueryVariablesSpecificMapRefactor("");
    setSelectedSpecificMapRefactor("");

    setQueryVariablesMapPoolRefactor("");
    setSelectedMapPoolRefactor("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    requestMatch({
      variables: {
        input: {
          bot1: selectedBot1Refactor,
          bot2: selectedBot2Refactor,
          matchCount: matchCount,
          mapSelectionType: mapSelectionType,
          chosenMap:
            mapSelectionType === "specific_map"
              ? selectedSpecificMapRefactor
              : undefined,
          mapPool:
            mapSelectionType === "map_pool"
              ? selectedMapPoolRefactor
              : undefined,
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
    if (!selectedBot1Refactor || !selectedBot2Refactor) {
      return false;
    }
    if (!matchCount || matchCount < 1) {
      return false;
    }

    if (mapSelectionType === "specific_map") {
      if (!selectedSpecificMapRefactor) {
        return false;
      }
    } else if (mapSelectionType === "map_pool") {
      if (!selectedMapPoolRefactor) {
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
        <div className="mb-4">
          <label className="block text-left font-medium mb-1">Bot 1</label>
          {bot1QueryRef ? (
            <SelectSearchListV2
              query={bot1Query}
              dataRef={bot1QueryRef}
              dataPath="bots.edges"
              onChangeRefactor={(value) => {
                setQueryVariablesBot1Refactor(value);
              }}
              onSelectRefactor={(value) => {
                setSelectedBot1Refactor(value);
              }}
              placeholder="Search for bots..."
            />
          ) : null}

          <label className="block text-left font-medium mb-1">Bot 2</label>
          {bot2QueryRef ? (
            <SelectSearchListV2
              query={bot2Query}
              dataRef={bot2QueryRef}
              dataPath="bots.edges"
              onChangeRefactor={(value) => {
                setQueryVariablesBot2Refactor(value);
              }}
              onSelectRefactor={(value) => {
                setSelectedBot2Refactor(value);
              }}
              placeholder="Search for bots..."
            />
          ) : null}
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
                <SelectSearchListV2
                  query={specificMapQuery}
                  dataRef={specificMapQueryRef}
                  dataPath="maps.edges"
                  onChangeRefactor={(value) => {
                    setQueryVariablesSpecificMapRefactor(value);
                  }}
                  onSelectRefactor={(value) => {
                    setSelectedSpecificMapRefactor(value);
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
                <SelectSearchListV2
                  query={mapPoolQuery}
                  dataRef={mapPoolQueryRef}
                  dataPath="mapPools.edges"
                  onChangeRefactor={(value) => {
                    setQueryVariablesMapPoolRefactor(value);
                  }}
                  onSelectRefactor={(value) => {
                    setSelectedMapPoolRefactor(value);
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
