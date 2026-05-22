import { useState } from "react";
import {
  ClipboardDocumentIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/20/solid";
import { useSnackbar } from "notistack";

interface TokenRevealProps {
  token: string | null | undefined;
  className?: string;
}

const MASK = "•••••••••••••••••••••••••••••••••••••••";

export default function TokenReveal({ token, className }: TokenRevealProps) {
  const { enqueueSnackbar } = useSnackbar();
  const [visible, setVisible] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(token ?? "");
    enqueueSnackbar("API token copied to clipboard!");
  };

  return (
    <div
      className={
        "flex items-center gap-2 bg-black text-gray-300 px-2 py-1 rounded font-mono text-xs break-words " +
        (className ?? "")
      }
    >
      <span className="flex-1 truncate">{visible ? token : MASK}</span>

      <button
        onClick={() => setVisible(!visible)}
        className="text-white hover:text-gray-400 p-1"
        title={visible ? "Hide token" : "Show token"}
      >
        {visible ? (
          <EyeSlashIcon className="h-4 w-4" />
        ) : (
          <EyeIcon className="h-4 w-4" />
        )}
      </button>

      <button
        onClick={handleCopy}
        className="text-white hover:text-gray-400 p-1"
        title="Copy token"
      >
        <ClipboardDocumentIcon className="h-4 w-4" />
      </button>
    </div>
  );
}
