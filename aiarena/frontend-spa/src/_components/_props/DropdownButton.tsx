export interface DropdownButtonProps {
  onClick: () => void;
  title: string;
  closeDropdown?: () => void;
}

export default function DropdownButton({
  onClick,
  title,
  closeDropdown,
}: DropdownButtonProps) {
  const handleClick = () => {
    onClick();
    closeDropdown?.();
  };

  return (
    <button
      className="w-full flex justify-between items-center px-3 py-2 text-left hover:bg-neutral-700 transition"
      onClick={handleClick}
    >
      <span>{title}</span>
    </button>
  );
}
