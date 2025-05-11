import Modal from "@/_components/_props/Modal";
import { useState } from "react";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { UploadBotModalQuery } from "./__generated__/UploadBotModalQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import {
  BotTypesEnum,
  UploadBotModalMutation,
} from "./__generated__/UploadBotModalMutation.graphql";
import Form from "@/_components/_props/Form";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

const BOT_TYPES: Record<BotTypesEnum, string> = {
  CPPWIN32: "cppwin32",
  CPPLINUX: "cpplinux",
  DOTNETCORE: "dotnetcore",
  JAVA: "java",
  NODEJS: "nodejs",
  PYTHON: "python",
  "%future added value": "future",
};

export default function UploadBotModal({ isOpen, onClose }: UploadBotModal) {
  const bot_race_data = useLazyLoadQuery<UploadBotModalQuery>(
    graphql`
      query UploadBotModalQuery {
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
  const bot_races = getNodes(bot_race_data.botRace);

  const [name, setName] = useState("");
  const [race, setRace] = useState(bot_races[0].id);
  const [type, setType] = useState<BotTypesEnum>(
    Object.keys(BOT_TYPES)[0] as BotTypesEnum
  );
  const [botZipFile, setBotZipFile] = useState<File | null>(null);

  const [botDataEnabled, setBotDataEnabled] = useState(false);

  const handlers = useSnackbarErrorHandlers(
    "uploadBot",
    "Bot Uploaded Succesfully!"
  );

  const [uploadBot, updating] = useMutation<UploadBotModalMutation>(graphql`
    mutation UploadBotModalMutation($input: UploadBotInput!) {
      uploadBot(input: $input) {
        bot {
          id
        }
        errors {
          field
          messages
        }
      }
    }
  `);

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Uploading Bot", { name, race, type, botDataEnabled });
    if (!name || !botZipFile || !race || !type) {
      return;
    }
    uploadBot({
      variables: {
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
      ...handlers,
    });
  };

  if (!isOpen) return null;

  return (
    <Modal onClose={onClose} title="Upload Bot">
      <Form
        handleSubmit={handleUpload}
        submitTitle="Upload Bot"
        loading={!updating}
      >
        <label className="block">
          <span className="text-gray-300">Name:</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full bg-gray-700 text-white p-2 rounded"
          />
        </label>

        <label className="block">
          <span className="text-gray-300">Bot ZIP:</span>
          <input
            type="file"
            className="w-full bg-gray-700 text-white p-2 rounded"
            required
            onChange={(e) => {
              if (e.target.files != null) {
                setBotZipFile(e.target.files[0]);
              } else {
                setBotZipFile(null);
              }
            }}
          />
        </label>

        <label className="block">
          <span className="text-gray-300">Bot Data Enabled:</span>
          <input
            type="checkbox"
            checked={botDataEnabled}
            onChange={(e) => setBotDataEnabled(e.target.checked)}
            className="ml-2"
          />
        </label>

        <label className="block">
          <span className="text-gray-300">Plays Race:</span>
          <select
            value={race}
            required
            onChange={(e) => {
              setRace(e.target.value);
            }}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            {bot_races.map((bot_race) => (
              <option key={bot_race.id} value={bot_race.id}>
                {bot_race.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-gray-300">Type:</span>
          <select
            required={true}
            value={type}
            onChange={(e) => {
              setType(e.target.value as BotTypesEnum);
              console.log(type);
            }}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            {Object.entries(BOT_TYPES)
              .filter((item) => item[0] != "%future added value")
              .map(([label]) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
          </select>
        </label>
      </Form>
    </Modal>
  );
}
