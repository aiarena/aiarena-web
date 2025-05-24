interface SearchbarProps {
  placeholder: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
}

export default function Searchbar({
  placeholder,
  onChange,
  value,
}: SearchbarProps) {
  return (
    <div className="mb-4 max-w-[40em]">
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full p-3 mb-2 border border-neutral-600 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-customGreen bg-darken-2 text-white placeholder-neutral-400"
      />
    </div>
  );
}
