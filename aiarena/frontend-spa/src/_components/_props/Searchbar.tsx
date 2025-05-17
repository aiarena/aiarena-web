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
        className="w-full p-3 mb-2 border border-gray-700 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-customGreen bg-gray-800 text-white placeholder-gray-500"
      />
    </div>
  );
}
