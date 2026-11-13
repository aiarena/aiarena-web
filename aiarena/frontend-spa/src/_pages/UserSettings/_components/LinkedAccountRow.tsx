import clsx from "clsx";

import SquareButton from "@/_components/_actions/SquareButton";

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
        <SquareButton onClick={onUnlink} color="red" text="Unlink" />
      ) : (
        <SquareButton onClick={onLink} text="Link" />
      )}
    </div>
  );
}
