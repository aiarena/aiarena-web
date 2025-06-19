import { ClipboardDocumentIcon } from "@heroicons/react/20/solid";
import { useSnackbar } from "notistack";
import React, { ReactNode, useRef } from "react";

interface CodeBoxCopyProps {
  children: ReactNode;
}

export const CodeBoxCopy: React.FC<CodeBoxCopyProps> = ({ children }) => {
  const { enqueueSnackbar } = useSnackbar();
  const preRef = useRef<HTMLPreElement>(null);

  const handleCopy = () => {
    const text = preRef.current?.innerText ?? "";
    navigator.clipboard.writeText(text).then(() => {
      const message =
        text.length > 15
          ? "Text copied to clipboard"
          : `"${text}" copied to clipboard!`;
      enqueueSnackbar(message);
    });
  };

  return (
    <div
      className="flex items-center min-h-[3em] group relative bg-black text-gray-100 font-mono rounded-lg overflow-auto p-2 cursor-pointer border-1 border-black hover:border-neutral-700"
      onClick={handleCopy}
      title="Copy text"
    >
      <span className="absolute top-2 right-2 group-hover:text-gray-400 text-xs px-2 py-1 rounded transition-colors duration-150">
        <ClipboardDocumentIcon className="h-4 w-4" />
      </span>

      <pre ref={preRef} className="whitespace-pre-wrap font-mono">
        {children}
      </pre>
    </div>
  );
};
