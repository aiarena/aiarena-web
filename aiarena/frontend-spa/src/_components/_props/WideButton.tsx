import LoadingSpinnerGray from "../_display/LoadingSpinnerGray";

interface WideButtonProps {
  loading?: boolean;
  title: string;
  type?: "button" | "submit" | "reset" | undefined;
}

export default function WideButton({
  loading = false,
  title,
  type = "button",
}: WideButtonProps) {
  return (
    <button
      disabled={loading}
      type={type}
      className="w-full bg-customGreen-dark text-white flex justify-center py-2 rounded border-2 border-customGreen-dark hover:bg-transparent hover:border-customGreen"
    >
      {loading ? <LoadingSpinnerGray /> : title}
    </button>
  );
}
