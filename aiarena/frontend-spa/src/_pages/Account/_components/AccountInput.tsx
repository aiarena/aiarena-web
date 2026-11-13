import clsx from "clsx";

interface AccountInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: "text" | "email" | "password";
  autoComplete?: string;
  autoFocus?: boolean;
  /** Backend messages for this field, shown under the input. */
  errors?: readonly string[];
}

export default function AccountInput({
  id,
  label,
  value,
  onChange,
  type = "text",
  autoComplete,
  autoFocus,
  errors = [],
}: AccountInputProps) {
  const errorId = `${id}-errors`;
  const hasErrors = errors.length > 0;

  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm text-gray-300">
        {label}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        autoFocus={autoFocus}
        required
        aria-invalid={hasErrors}
        aria-describedby={hasErrors ? errorId : undefined}
        className={clsx(
          "w-full rounded-sm p-2",
          hasErrors && "outline outline-1 outline-red-500",
        )}
      />
      {hasErrors && (
        <ul id={errorId} className="mt-1 space-y-0.5 text-sm text-red-400">
          {errors.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
