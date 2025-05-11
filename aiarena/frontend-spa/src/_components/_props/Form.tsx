import { ReactNode } from "react";
import LoadingSpinnerGray from "../_display/LoadingSpinnerGray";

interface FormProps {
  handleSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  submitTitle: string;
  children: ReactNode;
}

export default function Form({
  handleSubmit,
  loading,
  submitTitle = "",
  children,
}: FormProps) {
  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {children}
      <button
        type="submit"
        className="w-full bg-customGreen text-white py-2 rounded "
      >
        {loading ? <LoadingSpinnerGray /> : submitTitle}
      </button>
    </form>
  );
}
