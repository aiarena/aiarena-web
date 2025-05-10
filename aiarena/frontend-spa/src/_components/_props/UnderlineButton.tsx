import { ReactNode } from "react";

interface UnderlineButtonProps {
  children: ReactNode;
  onClick: () => void;
}
export default function UnderlineButton({
  children,
  onClick,
}: UnderlineButtonProps) {
  return (
    <button
      onClick={() => onClick}
      className="mt-2 text-customGreen underline hover:text-white"
    >
      {children}
    </button>
  );
}
