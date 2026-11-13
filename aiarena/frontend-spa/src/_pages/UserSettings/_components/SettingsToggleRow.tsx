import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";

interface SettingsToggleRowProps {
  label: string;
  enabled: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
}

export default function SettingsToggleRow({
  label,
  enabled,
  onChange,
  disabled,
}: SettingsToggleRowProps) {
  return (
    <div className="flex items-center justify-between gap-4 bg-black text-gray-300 px-2 py-2 rounded text-sm">
      <span>{label}</span>
      <SimpleToggle enabled={enabled} onChange={onChange} disabled={disabled} />
    </div>
  );
}
