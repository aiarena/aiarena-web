import React from "react";
import Modal from "@/_components/_actions/Modal";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { RequestMatchModalMutation } from "./__generated__/RequestMatchModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import Form from "@/_components/_actions/Form";
import { useRelayConnectionID } from "@/_components/_contexts/RelayConnectionIDContext/useRelayConnectionID";
import { CONNECTION_KEYS } from "@/_components/_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";
import BotSearchList, {
  BotType,
} from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/BotSearchList";
import MapSearchList, {
  MapType,
} from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/MapSearchList";
import MapPoolSearchList, {
  MapPoolType,
} from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/MapPoolSearchList";
import clsx from "clsx";
import { RequestMatchModalQuery } from "./__generated__/RequestMatchModalQuery.graphql";
import useStateWithSessionStorage from "@/_components/_hooks/useStateWithSessionStorage";
import { useSnackbar } from "notistack";

// Mirrors MAX_LENGTH in aiarena/core/bot_args.py — the server rejects anything longer.
const BOT_ARGS_MAX_LENGTH = 500;

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function RequestMatchModal({ isOpen, onClose }: UploadBotModal) {
  const { getConnectionID } = useRelayConnectionID();
  const connectionID = getConnectionID(
    CONNECTION_KEYS.UserMatchRequestsConnection,
  );

  const [mapSelectionType, setMapSelectionType] = useStateWithSessionStorage<
    "map_pool" | "specific_map"
  >("mapSelectionType", "map_pool");

  const [matchCount, setMatchCount] = useStateWithSessionStorage<string>(
    "matchCount",
    "1",
  );

  const [selectedBot1, setSelectedBot1] =
    useStateWithSessionStorage<BotType>("bot1");

  const [selectedBot2, setSelectedBot2] =
    useStateWithSessionStorage<BotType>("bot2");

  const [selectedSpecificMap, setSelectedSpecificMap] =
    useStateWithSessionStorage<MapType | null>("selectedMap");

  const [selectedMapPool, setSelectedMapPool] =
    useStateWithSessionStorage<MapPoolType | null>("mapPool");

  const [bot1Args, setBot1Args] = useStateWithSessionStorage<string>(
    "bot1Args",
    "",
  );

  const [bot2Args, setBot2Args] = useStateWithSessionStorage<string>(
    "bot2Args",
    "",
  );

  const data = useLazyLoadQuery<RequestMatchModalQuery>(
    graphql`
      query RequestMatchModalQuery {
        viewer {
          requestMatchBotArgsEnabled
        }
        ...BotSearchList
        ...MapPoolSearchList
        ...MapSearchList
      }
    `,
    {},
  );

  const botArgsEnabled = data.viewer?.requestMatchBotArgsEnabled ?? false;

  const [requestMatch, updating] = useMutation<RequestMatchModalMutation>(
    graphql`
      mutation RequestMatchModalMutation(
        $input: RequestMatchInput!
        $connections: [ID!]!
      ) {
        requestMatch(input: $input) {
          viewer {
            requestMatchesCountLeft
          }
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
    `,
  );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "requestMatch",
    "Match Requested!",
  );

  const { enqueueSnackbar } = useSnackbar();

  function isEmptyOrZero(raw: string | null | undefined): boolean {
    if (raw == null) return true;
    const v = raw.trim();
    return v === "" || v === "0";
  }

  function hasLetters(value: string | null): boolean {
    if (isEmptyOrZero(value) || value === null) return false;
    return /[A-Za-z]/.test(value);
  }

  const checkMatchCount = (value: string | null) => {
    if (isEmptyOrZero(value) || value === null) {
      setMatchCount("1");
      enqueueSnackbar(
        <span className="overflow-auto">
          {"Match count was 0 or null, we changed it to 1, try re-requesting."}
        </span>,
        { variant: "error" },
      );
      return false;
    }
    if (hasLetters(value) && value !== null) {
      setMatchCount(`${parseInt(value.replace(/\D/g, ""))}`);
      enqueueSnackbar(
        <span className="overflow-auto">
          {
            "Match count can't be a letter, we removed it for you, try re-requesting."
          }
        </span>,
        { variant: "error" },
      );
      return false;
    }
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const validMatchCount = checkMatchCount(matchCount);
    if (validMatchCount) {
      requestMatch({
        variables: {
          connections: [connectionID],
          input: {
            bot1: selectedBot1?.id,
            bot2: selectedBot2?.id,
            matchCount: parseInt(matchCount || "0"),
            mapSelectionType: mapSelectionType,
            chosenMap:
              mapSelectionType === "specific_map"
                ? selectedSpecificMap?.id
                : undefined,
            mapPool:
              mapSelectionType === "map_pool" ? selectedMapPool?.id : undefined,
            bot1Args: botArgsEnabled ? bot1Args?.trim() || "" : "",
            bot2Args: botArgsEnabled ? bot2Args?.trim() || "" : "",
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
    }
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
              setValue={setSelectedBot1}
              relayRootQuery={data}
            />
          </label>

          <label className="flex flex-col gap-1">
            <span id="opponent-name" className="font-medium">
              Opponent
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
              value={matchCount || undefined}
              type="text"
              onChange={(e) => {
                setMatchCount(e.target.value || " ");
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
                setMapSelectionType("map_pool");
              }}
              className={clsx(
                "border-2 mr-2 rounded-lg bg-darken p-2",
                mapSelectionType === "map_pool"
                  ? "border-customGreen"
                  : "border-gray-700 hover:bg-transparent hover:border-customGreen",
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
                  : "border-gray-700 hover:bg-transparent hover:border-customGreen",
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

        {botArgsEnabled ? (
          <div className="mt-4 flex flex-col gap-2">
            <label className="flex flex-col gap-1">
              <span className="font-medium">Bot 1 Arguments</span>
              <input
                type="text"
                value={bot1Args ?? ""}
                maxLength={BOT_ARGS_MAX_LENGTH}
                placeholder={'--build="example build"'}
                onChange={(e) => setBot1Args(e.target.value)}
                aria-describedby="bot-args-help"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="font-medium">Bot 2 Arguments</span>
              <input
                type="text"
                value={bot2Args ?? ""}
                maxLength={BOT_ARGS_MAX_LENGTH}
                placeholder={'--opponent="example opponent"'}
                onChange={(e) => setBot2Args(e.target.value)}
                aria-describedby="bot-args-help"
              />
            </label>

            <span id="bot-args-help" className="text-sm text-gray-400">
              Optional. Each is passed to that bot verbatim as extra command
              line arguments, split the way a shell would — so quote to include
              spaces: <code>--message=&quot;good luck&quot;</code>. Arguments
              the arena client sets itself can&apos;t be overridden.
            </span>
          </div>
        ) : null}
      </Form>
    </Modal>
  );
}
