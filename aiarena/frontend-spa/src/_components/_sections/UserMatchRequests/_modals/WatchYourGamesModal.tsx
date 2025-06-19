import { CodeBoxCopy } from "@/_components/_actions/CodeBoxCopy";
import Modal from "@/_components/_actions/Modal";
import WatchYourGamesButton from "@/_components/_actions/WatchYourGamesButton";
import SectionDivider from "@/_components/_display/SectionDivider";

import GetGameOfInterest from "../GetGameOfInterest";
import { Suspense } from "react";

import LoadingDots from "@/_components/_display/LoadingDots";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function WatchYourGamesModal({
  isOpen,
  onClose,
}: UploadBotModal) {
  return (
    <Modal onClose={onClose} isOpen={isOpen} title="Watch Games on Twitch">
      <div className="mb-6">
        <ol className="space-y-4 ">
          <li className="flex flex-col gap-2">
            <span id="visit-aiarena-twitch" className="font-medium">
              Visit the <span className="font-gugi">AI Arena</span> stream
            </span>
            <WatchYourGamesButton href="https://www.twitch.tv/aiarenastream">
              <span className="font-gugi font-light">AI Arena</span>
            </WatchYourGamesButton>
          </li>
          <li className="flex flex-col gap-2">
            <span id="queue-match-command" className="font-medium">
              Queue your match
            </span>
            <CodeBoxCopy>
              <Suspense fallback={<LoadingDots />}>
                <GetGameOfInterest />
              </Suspense>
            </CodeBoxCopy>
          </li>
          <li className="flex flex-col gap-2">
            <span id="skip-current-match-command" className="font-medium">
              Skip the current match
            </span>
            <CodeBoxCopy>!next</CodeBoxCopy>
          </li>
        </ol>

        <SectionDivider color="gray" className="my-6 pb-1" />

        <div
          role="group"
          aria-labelledby="other-commands-label"
          className="flex flex-col gap-2"
        >
          <span id="other-commands-label" className="font-medium">
            Other commands
          </span>
          <CodeBoxCopy>!help</CodeBoxCopy>
        </div>
      </div>
    </Modal>
  );
}
