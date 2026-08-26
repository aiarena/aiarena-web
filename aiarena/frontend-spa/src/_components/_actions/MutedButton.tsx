import { ReactNode } from "react";

export default function MutedButton({
  onClick,
  children,
  title,
}: {
  onClick: () => void;
  children: ReactNode;
  title: string;
  className?: string;
}) {
  return (
    <button
      className="cursor-pointer hover:bg-neutral-900 hover:border-neutral-500 py-1 px-2 ml-2 flex justify-center rounded-md gap-2 border border-neutral-600 items-center shadow-sm shadow-black w-full"
      onClick={onClick}
      title={title}
    >
      {children}
    </button>
  );
}
