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

  const getBot1 = () => {
    const bot1 = sessionStorage.getItem("bot1");
    return bot1 != null ? JSON.parse(bot1) : null;
  };
  const getBot2 = () => {
    const bot2 = sessionStorage.getItem("bot2");
    return bot2 != null ? JSON.parse(bot2) : null;
  };

  const getMapSelectionType = () => {
    const mapSelectionType = sessionStorage.getItem("mapSelectionType");
    return mapSelectionType != null ? JSON.parse(mapSelectionType) : "map_pool";
  };

  const getMapPool = () => {
    const mapPool = sessionStorage.getItem("mapPool");
    return mapPool != null ? JSON.parse(mapPool) : null;
  };

  const getSpecificMap = () => {
    const specificMap = sessionStorage.getItem("selectedMap");
    return specificMap != null ? JSON.parse(specificMap) : null;
  };

  const getMatchCount = () => {
    const matchCount = sessionStorage.getItem("matchCount");
    return matchCount != null ? JSON.parse(matchCount) : 1;
  };

  const [mapSelectionType, setMapSelectionType] = useState(
    getMapSelectionType()
  );
  const [matchCount, setMatchCount] = useState(getMatchCount());
  const [selectedBot1, setSelectedBot1] = useState<BotType | null>(getBot1());
  const [selectedBot2, setSelectedBot2] = useState<BotType | null>(getBot2());
  const [selectedSpecificMap, setSelectedSpecificMap] =
    useState<MapType | null>(getSpecificMap());
  const [selectedMapPool, setSelectedMapPool] = useState<MapPoolType | null>(
    getMapPool()
  );

  const setAndSaveBot1 = (bot: BotType | null) => {
    setSelectedBot1(bot);
    sessionStorage.setItem("bot1", JSON.stringify(bot));
  };

  const setAndSaveBot2 = (bot: BotType | null) => {
    setSelectedBot2(bot);
    sessionStorage.setItem("bot2", JSON.stringify(bot));
  };

  const setAndSaveSpecificMap = (map: MapType | null) => {
    setSelectedSpecificMap(map);
    sessionStorage.setItem("selectedMap", JSON.stringify(map));
  };

  const setAndSaveMapPool = (mapPool: MapPoolType | null) => {
    setSelectedMapPool(mapPool);
    sessionStorage.setItem("mapPool", JSON.stringify(mapPool));
  };

  const setAndSaveMapSelectionType = (type: "map_pool" | "specific_map") => {
    setMapSelectionType(type);
    sessionStorage.setItem("mapSelectionType", JSON.stringify(type));
  };

  const setAndSaveMatchCount = (count: number) => {
    setMatchCount(count);
    sessionStorage.setItem("matchCount", JSON.stringify(count));
  };

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    requestMatch({
      variables: {
        connections: [connectionID],
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
            <span id="bot-name" className="font-medium">
              Bot
            </span>
            <BotSearchList
              value={selectedBot1}
              setValue={setAndSaveBot1}
              relayRootQuery={data}
            />
          </label>

          <label className="flex flex-col gap-1">
            <span id="opponent-name" className="font-medium">
              Opponent
            </span>
            <BotSearchList
              value={selectedBot2}
              setValue={setAndSaveBot2}
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
              type="number"
              onChange={(e) => {
                const value = parseInt(e.target.value.replace(/\D/g, "")) || 0;
                setAndSaveMatchCount(value);
              }}
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
                setAndSaveMapSelectionType("map_pool");
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
                setAndSaveMapSelectionType("specific_map");
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
                setValue={setAndSaveMapPool}
                relayRootQuery={data}
              />
            </label>
          ) : null}

          {mapSelectionType === "specific_map" ? (
            <label className="mb-16 flex flex-col gap-1">
              <span className="font-medium">Specific Map</span>
              <MapSearchList
                value={selectedSpecificMap}
                setValue={setAndSaveSpecificMap}
                relayRootQuery={data}
              />
            </label>
          ) : null}
        </div>
      </Form>
    </Modal>
  );
}
