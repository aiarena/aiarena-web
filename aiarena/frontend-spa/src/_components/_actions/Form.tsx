import { ReactNode } from "react";
import WideButton from "./WideButton";

interface FormProps {
  handleSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  submitTitle: string;
  children: ReactNode;
  disabled?: boolean;
}

export default function Form({
  handleSubmit,
  loading,
  submitTitle = "",
  children,
  disabled = false,
}: FormProps) {
  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {children}
      <WideButton
        title={submitTitle}
        loading={loading}
        type="submit"
        disabled={disabled}
      />
    </form>
  );
}
