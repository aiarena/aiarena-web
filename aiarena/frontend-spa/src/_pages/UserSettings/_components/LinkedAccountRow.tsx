import { useState } from "react";
import clsx from "clsx";

import SquareButton from "@/_components/_actions/SquareButton";
import ConfirmModal from "@/_components/_actions/ConfirmModal";

interface LinkedAccountRowProps {
  name: string;
  iconPath: string | undefined;
  invertIcon?: boolean;
  linked: boolean;
  onLink: () => void;
  onUnlink: () => void;
}

export default function LinkedAccountRow({
  name,
  iconPath,
  invertIcon,
  linked,
  onLink,
  onUnlink,
}: LinkedAccountRowProps) {
  const [confirmingUnlink, setConfirmingUnlink] = useState(false);

  return (
    <div className="flex items-center justify-between gap-4 bg-black text-gray-300 px-2 py-2 rounded text-sm">
      <span className="flex items-center gap-2">
        {iconPath && (
          <img
            src={iconPath}
            alt=""
            width={20}
            height={20}
            className={clsx("w-5 h-5", invertIcon && "invert")}
          />
        )}
        <span>{name}</span>
        <span className={linked ? "text-customGreen" : "text-gray-500"}>
          {linked ? "· Linked" : "· Not linked"}
        </span>
      </span>
      {linked ? (
        <SquareButton
          onClick={() => setConfirmingUnlink(true)}
          color="red"
          text="Unlink"
        />
      ) : (
        <SquareButton onClick={onLink} text="Link" />
      )}
      <ConfirmModal
        isOpen={confirmingUnlink}
        onClose={() => setConfirmingUnlink(false)}
        onConfirm={onUnlink}
        title={`Unlink ${name}?`}
        confirmText="Unlink"
      >
        <p>
          Your AI Arena account will no longer be connected to your {name}{" "}
          account. You can link it again at any time.
        </p>
      </ConfirmModal>
    </div>
  );
}
