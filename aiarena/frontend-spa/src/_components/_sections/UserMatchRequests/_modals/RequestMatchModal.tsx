import React, { useState } from "react";
import Modal from "@/_components/_actions/Modal";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_actions/Form";
import { useRelayConnectionID } from "@/_components/_contexts/RelayConnectionIDContext/useRelayConnectionID";
import { CONNECTION_KEYS } from "@/_components/_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";

import BotSearchList, {
  BotType,
} from "@/_components/_sections/UserMatchRequests/_modals/BotSearchList";
import MapSearchList, {
  MapType,
} from "@/_components/_sections/UserMatchRequests/_modals/MapSearchList";
import MapPoolSearchList, {
  MapPoolType,
} from "@/_components/_sections/UserMatchRequests/_modals/MapPoolSearchList";
import clsx from "clsx";
import { RequestMatchModalQuery } from "./__generated__/RequestMatchModalQuery.graphql";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function RequestMatchModal({ isOpen, onClose }: UploadBotModal) {
  const { getConnectionID } = useRelayConnectionID();
  const connectionID = getConnectionID(
    CONNECTION_KEYS.UserMatchRequestsConnection
  );

  const [mapSelectionType, setMapSelectionType] = useState("map_pool");
  const [matchCount, setMatchCount] = useState(1);
  const [selectedBot1, setSelectedBot1] = useState<BotType | null>(null);
  const [selectedBot2, setSelectedBot2] = useState<BotType | null>(null);
  const [selectedSpecificMap, setSelectedSpecificMap] =
    useState<MapType | null>(null);
  const [selectedMapPool, setSelectedMapPool] = useState<MapPoolType | null>(
    null
  );

  const data = useLazyLoadQuery<RequestMatchModalQuery>(
    graphql`
      query RequestMatchModalQuery {
        ...BotSearchList
        ...MapPoolSearchList
        ...MapSearchList
      }
    `,
    {}
  );

  const [requestMatch, updating] = useMutation<RequestMatchModalMutation>(
    graphql`
      mutation RequestMatchModalMutation(
        $input: RequestMatchInput!
        $connections: [ID!]!
      ) {
        requestMatch(input: $input) {
          match
            @prependNode(
              connections: $connections
              edgeTypeName: "MatchTypeEdge"
            ) {
            id
            participant1 {
              id
              name
            }
            participant2 {
              id
              name
            }
            result {
              type
              winner {
                name
              }
            }
            map {
              name
            }
            tags {
              edges {
                node {
                  id
                  tag
                  user {
                    id
                  }
                }
              }
            }
            started
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
    "Match Requested!"
  );

  const resetAllStateFields = () => {
    setMapSelectionType("map_pool");
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
        connections: [connectionID],
        input: {
          agent1: selectedBot1?.id,
          agent2: selectedBot2?.id,
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
          <label className="flex flex-col gap-1 ">
            <span id="agent1-name" className="font-medium">
              Agent 1
            </span>
            <BotSearchList
              value={selectedBot1}
              setValue={setSelectedBot1}
              relayRootQuery={data}
            />
          </label>

          <label className="flex flex-col gap-1">
            <span id="agent2-name" className="font-medium">
              Agent 2
            </span>
            <BotSearchList
              value={selectedBot2}
              setValue={setSelectedBot2}
              relayRootQuery={data}
            />
          </label>
        </div>

        <div className="mb-4"></div>
        <div className="flex flex-wrap gap-4">
          <div className="flex">
            <label className="block text-left mb-1 pt-2 pr-2 font-medium">
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
              Number of games to play between selected agents
            </div>
          </div>

          <div className="block">
            <button
              type="button"
              onClick={() => {
                setMapSelectionType("map_pool");
              }}
              className={clsx(
                "border-2 mr-2 rounded-lg bg-darken p-2",
                mapSelectionType === "map_pool"
                  ? "border-customGreen"
                  : "border-gray-700 hover:bg-transparent hover:border-customGreen"
              )}
            >
              Map Pool
            </button>

            <button
              type="button"
              onClick={() => {
                setMapSelectionType("specific_map");
              }}
              className={clsx(
                "border-2 rounded-lg bg-darken p-2",
                mapSelectionType === "specific_map"
                  ? "border-customGreen"
                  : "border-gray-700 hover:bg-transparent hover:border-customGreen"
              )}
            >
              Specific Map
            </button>
          </div>
        </div>

        <div>
          {mapSelectionType === "map_pool" ? (
            <label className="mb-16 flex flex-col gap-1">
              <span className="font-medium">Map pool</span>
              <MapPoolSearchList
                value={selectedMapPool}
                setValue={setSelectedMapPool}
                relayRootQuery={data}
              />
            </label>
          ) : null}

          {mapSelectionType === "specific_map" ? (
            <label className="mb-16 flex flex-col gap-1">
              <span className="font-medium">Specific Map</span>
              <MapSearchList
                value={selectedSpecificMap}
                setValue={setSelectedSpecificMap}
                relayRootQuery={data}
              />
            </label>
          ) : null}
        </div>
      </Form>
    </Modal>
  );
}
