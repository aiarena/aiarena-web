import clsx from "clsx";

interface SearchbarProps {
  placeholder: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
  isLoading: boolean;
}

export default function Searchbar({
  placeholder,
  onChange,
  value,
  isLoading,
}: SearchbarProps) {
  return (
    <div className="mb-4 max-w-[40em]">
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={clsx(
          "w-full",
          "p-3",
          "mb-2",
          "border",
          "rounded",
          "shadow-sm",
          "focus:outline-none",
          "focus:ring-2",
          "focus:ring-customGreen",
          "bg-darken-2",
          "text-white",
          "placeholder-neutral-400",
          {
            "border-customGreen animate-border-fade-in-out": isLoading,
            "border-neutral-600": !isLoading,
          }
        )}
      />
    </div>
  );
}
