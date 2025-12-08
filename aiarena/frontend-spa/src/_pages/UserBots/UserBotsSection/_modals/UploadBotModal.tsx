import Modal from "@/_components/_actions/Modal";
import { useState } from "react";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { UploadBotModalQuery } from "./__generated__/UploadBotModalQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { UploadBotModalMutation } from "./__generated__/UploadBotModalMutation.graphql";
import Form from "@/_components/_actions/Form";
import { UploadFile } from "@/_components/_actions/UploadFile";
import { useRelayConnectionID } from "@/_components/_contexts/RelayConnectionIDContext/useRelayConnectionID";
import { CONNECTION_KEYS } from "@/_components/_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";
import { BOT_TYPES } from "@/_data/BOT_TYPES";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

type Race = "P" | "R" | "T" | "Z";

export default function UploadBotModal({ isOpen, onClose }: UploadBotModal) {
  const { getConnectionID } = useRelayConnectionID();
  const connectionID = getConnectionID(CONNECTION_KEYS.UserBotsConnection);

  const data = useLazyLoadQuery<UploadBotModalQuery>(
    graphql`
      query UploadBotModalQuery {
        viewer {
          user {
            id
          }
        }

        botRace {
          edges {
            node {
              id
              label
              name
            }
          }
        }
      }
    `,
    {}
  );

  const bot_races = getNodes(data.botRace);

  const [name, setName] = useState("");
  const [race, setRace] = useState<Race>("P");
  const [type, setType] = useState(Object.keys(BOT_TYPES)[0]);
  const [botZipFile, setBotZipFile] = useState<File | null>(null);

  const [botDataEnabled, setBotDataEnabled] = useState(false);
  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "uploadBot",
    "Bot Uploaded Successfully!"
  );

  const [uploadBot, updating] = useMutation<UploadBotModalMutation>(graphql`
    mutation UploadBotModalMutation(
      $input: UploadBotInput!
      $connections: [ID!]!
    ) {
      uploadBot(input: $input) {
        bot
          @prependNode(connections: $connections, edgeTypeName: "BotTypeEdge") {
          id
          name
          created
          type
          url
          botData
          botDataEnabled
          botDataPubliclyDownloadable
          botZip
          botZipPubliclyDownloadable
          botZipUpdated
          wikiArticle
          trophies {
            edges {
              node {
                name
                trophyIconImage
                trophyIconName
              }
            }
          }
        }
        errors {
          field
          messages
        }
      }
    }
  `);

  const resetAllStateFields = () => {
    setName("");
    setRace("P");
    setType(Object.keys(BOT_TYPES)[0]);
    setBotZipFile(null);
    setBotDataEnabled(false);
  };

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !botZipFile || !race || !type || !data.viewer?.user?.id) {
      return;
    }
    uploadBot({
      variables: {
        connections: [connectionID],
        input: {
          playsRace: race,
          botDataEnabled: botDataEnabled,
          name: name,
          type: type,
          botZip: null,
        },
      },
      uploadables: {
        "input.botZip": botZipFile,
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
    if (!name.trim()) {
      return false;
    }
    if (!race) {
      return false;
    }

    if (!type) {
      return false;
    }
    if (!botZipFile) {
      return false;
    }
    if (!data.viewer?.user?.id) {
      return false;
    }

    return true;
  };

  return (
    <Modal onClose={onClose} isOpen={isOpen} title="Upload Bot">
      <Form
        handleSubmit={handleUpload}
        submitTitle="Upload Bot"
        loading={updating}
        disabled={!isFormValid()}
      >
        <fieldset>
          <legend className="sr-only">Bot Upload Information</legend>

          <div className="block mb-4">
            <label htmlFor="bot-name" className="block mb-2">
              <span className="text-gray-300">Name:</span>
            </label>
            <input
              id="bot-name"
              name="bot-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="off"
              className="w-full p-2"
              aria-describedby="bot-name-help"
              placeholder="Enter your bot's name"
            />
            <div id="bot-name-help" className="sr-only">
              Choose a unique name for your bot
            </div>
          </div>

          <div className="block mb-4">
            <label htmlFor="bot-zip" className="block mb-2">
              <span className="text-gray-300">Bot ZIP:</span>
            </label>
            <UploadFile
              id="bot-zip"
              accept=".zip"
              file={botZipFile}
              setFile={setBotZipFile}
              required
              aria-describedby="bot-zip-help"
            />
            <div id="bot-zip-help" className="sr-only">
              Upload a ZIP file containing your bot's code and resources
            </div>
          </div>

          <div className="mb-4">
            <fieldset>
              <div className="inline-flex items-center">
                <label htmlFor="bot-data-enabled" className="text-gray-300">
                  Enable Bot Data:
                </label>
                <input
                  id="bot-data-enabled"
                  name="bot-data-enabled"
                  type="checkbox"
                  checked={botDataEnabled}
                  onChange={(e) => setBotDataEnabled(e.target.checked)}
                  className="w-5 h-5 ml-2"
                  aria-describedby="bot-data-help"
                />
              </div>
              <div id="bot-data-help" className="sr-only">
                Allow your bot to store and access persistent data between
                matches
              </div>
            </fieldset>
          </div>

          <div className="block mb-4">
            <label htmlFor="bot-race" className="block mb-2">
              <span className="text-gray-300">Plays Race:</span>
            </label>
            <select
              id="bot-race"
              name="bot-race"
              value={race}
              required
              onChange={(e) => {
                setRace(e.target.value as Race);
              }}
              autoComplete="off"
              className="w-full p-2"
              aria-describedby="bot-race-help"
            >
              <option value="" disabled>
                Select a race
              </option>
              {bot_races.map((bot_race) => (
                <option key={bot_race.id} value={bot_race.label}>
                  {bot_race.name}
                </option>
              ))}
            </select>
            <div id="bot-race-help" className="sr-only">
              Choose which game race your bot is designed to play
            </div>
          </div>

          <div className="block mb-4">
            <label htmlFor="bot-type" className="block mb-2">
              <span className="text-gray-300">Type:</span>
            </label>
            <select
              id="bot-type"
              name="bot-type"
              required={true}
              value={type}
              onChange={(e) => {
                setType(e.target.value);
              }}
              autoComplete="off"
              className="w-full p-2"
              aria-describedby="bot-type-help"
            >
              <option value="" disabled>
                Select bot type
              </option>
              {Object.entries(BOT_TYPES).map(([label, value]) => (
                <option key={label} value={label.toLowerCase()}>
                  {value.name}
                </option>
              ))}
            </select>
            <div id="bot-type-help" className="sr-only">
              Select the type of bot you are uploading
            </div>
          </div>
        </fieldset>
      </Form>
    </Modal>
  );
}
