import Modal from "@/_components/_actions/Modal";
import { graphql, useFragment } from "react-relay";
import { BotTrophiesModal_bot$key } from "./__generated__/BotTrophiesModal_bot.graphql";
import { getNodes } from "@/_lib/relayHelpers";

interface TrophiesModalProps {
  bot: BotTrophiesModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function BotTrophiesModal(props: TrophiesModalProps) {
  const bot = useFragment(
    graphql`
      fragment BotTrophiesModal_bot on BotType {
        id
        name
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
    `,
    props.bot,
  );

  if (!props.isOpen) return null;
  const trophies = getNodes(bot.trophies);

  return (
    <Modal
      onClose={props.onClose}
      isOpen={props.isOpen}
      title={`Trophies - ${bot.name}`}
    >
      <div className="p-4">
        {bot.trophies && trophies.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {trophies.map((trophy, index) => (
              <div
                key={index}
                className="flex flex-col items-center p-3 bg-darken-6 border border-customGreen shadow-lg shadow-customGreen-dark rounded-md"
              >
                <div className="w-12 h-12 relative mb-2">
                  <img
                    src={`${trophy.trophyIconImage}`}
                    alt={trophy.name}
                    style={{ objectFit: "contain" }}
                  />
                </div>
                <p className="text-xs text-gray-300 text-center">
                  {trophy.name}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center">
            <p className="text-sm text-gray-300 mb-4">
              No trophies yet. Compete in competitions to earn trophies.
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
}
