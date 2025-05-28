import React, { useEffect, useState } from "react";
import Modal from "@/_components/_props/Modal";
import { graphql, useMutation, useQueryLoader } from "react-relay";

import { RequestMatchModalBot1Query } from "./__generated__/RequestMatchModalBot1Query.graphql";

import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_props/Form";

import { RequestMatchModalBot2Query } from "./__generated__/RequestMatchModalBot2Query.graphql";
import { RequestMatchModalSpecificMapQuery } from "./__generated__/RequestMatchModalSpecificMapQuery.graphql";
import { RequestMatchModalMapPoolQuery } from "./__generated__/RequestMatchModalMapPoolQuery.graphql";
import SelectSearchList from "@/_components/_props/SelectSearchList";

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

  const [queryVariablesBot1, setQueryVariablesBot1] = useState("");
  const [selectedBot1, setSelectedBot1] = useState("");

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
    loadBot1Query({ name: queryVariablesBot1 });
  }, [queryVariablesBot1, loadBot1Query]);

  // Bot 2 Query
  // ____________________

  const [queryVariablesBot2, setQueryVariablesBot2] = useState("");
  const [selectedBot2, setSelectedBot2] = useState("");

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
    loadBot2Query({ name: queryVariablesBot2 });
  }, [queryVariablesBot2, loadBot2Query]);

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
    `
  );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "requestMatch",
    "Match Request Updated!"
  );

  const resetAllStateFields = () => {
    setMapSelectionType("specific_map");
    setMatchCount(1);

    setQueryVariablesBot1("");
    setSelectedBot1("");

    setQueryVariablesBot2("");
    setSelectedBot2("");

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
          bot1: selectedBot1,
          bot2: selectedBot2,
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
        <div className="mb-4">
          <label className="block text-left font-medium mb-1">Bot 1</label>
          {bot1QueryRef ? (
            <SelectSearchList
              query={bot1Query}
              dataRef={bot1QueryRef}
              dataPath="bots.edges"
              onChange={(value) => {
                setQueryVariablesBot1(value);
              }}
              onSelect={(value) => {
                setSelectedBot1(value);
              }}
              placeholder="Search for bots..."
            />
          ) : null}

          <label className="block text-left font-medium mb-1">Bot 2</label>
          {bot2QueryRef ? (
            <SelectSearchList
              query={bot2Query}
              dataRef={bot2QueryRef}
              dataPath="bots.edges"
              onChange={(value) => {
                setQueryVariablesBot2(value);
              }}
              onSelect={(value) => {
                setSelectedBot2(value);
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
