import Modal from "@/_components/_props/Modal";
import { useState } from "react";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { UploadBotModalQuery } from "./__generated__/UploadBotModalQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { UploadBotModalMutation } from "./__generated__/UploadBotModalMutation.graphql";
import Form from "@/_components/_props/Form";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

type Race = "P" | "R" | "T" | "Z";

const BOT_TYPES: Record<string, string> = {
  cppwin32: "C++ (Windows)",
  cpplinux: "C++ (Linux)",
  dotnetcore: ".NET Core",
  java: "Java",
  nodejs: "Node.js",
  python: "Python",
};

export default function UploadBotModal({ isOpen, onClose }: UploadBotModal) {
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
    {},
  );
  const bot_races = getNodes(data.botRace);

  const [name, setName] = useState("");
  const [race, setRace] = useState<Race>("P");
  const [type, setType] = useState(Object.keys(BOT_TYPES)[0]);
  const [botZipFile, setBotZipFile] = useState<File | null>(null);

  const [botDataEnabled, setBotDataEnabled] = useState(false);

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "uploadBot",
    "Bot Uploaded Successfully!",
  );

  const [uploadBot, updating] = useMutation<UploadBotModalMutation>(graphql`
    mutation UploadBotModalMutation($input: UploadBotInput!, $userId: ID!) {
      uploadBot(input: $input) {
        node(id: $userId) {
          ... on UserType {
            ...ProfileBotOverviewList_user
          }
        }
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

  // also sort on userbots
  // redirect on logged out

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !botZipFile || !race || !type || !data.viewer?.user?.id) {
      return;
    }
    uploadBot({
      variables: {
        userId: data.viewer.user.id,
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
          onClose();
        }
      },
      onError,
    });
  };
  return (
    <Modal onClose={onClose} isOpen={isOpen} title="Upload Bot">
      <Form
        handleSubmit={handleUpload}
        submitTitle="Upload Bot"
        loading={updating}
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
              setRace(e.target.value as Race);
            }}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            {bot_races.map((bot_race) => (
              <option key={bot_race.id} value={bot_race.label}>
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
              setType(e.target.value);
            }}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            {Object.entries(BOT_TYPES).map(([label, value]) => (
              <option key={label} value={label}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </Form>
    </Modal>
  );
}
