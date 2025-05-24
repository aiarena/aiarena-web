import LoadingSpinnerGray from "../_display/LoadingSpinnerGray";

interface WideButtonProps {
  loading?: boolean;
  title: string;
  type?: "button" | "submit" | "reset" | undefined;
  onClick?: () => void;
  style?: string;
}

export default function WideButton({
  loading = false,
  title,
  type = "button",
  onClick,
  style,
}: WideButtonProps) {
  return (
    <button
      disabled={loading}
      type={type}
      onClick={onClick}
      className={`w-full shadow-sm shadow-black hover:shadow-none border-2 border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent text-white font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform ${style} ${loading ? "py-2.5" : "py-2"}`}
    >
      {loading ? <LoadingSpinnerGray /> : title}
    </button>
  );
}
