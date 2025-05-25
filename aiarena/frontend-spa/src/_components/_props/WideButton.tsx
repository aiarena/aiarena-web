import LoadingSpinner from "../_display/LoadingSpinnerGray";

interface WideButtonProps {
  loading?: boolean;
  title: string;
  type?: "button" | "submit" | "reset" | undefined;
  onClick?: () => void;
  style?: string;
  disabled?: boolean;
}

export default function WideButton({
  loading = false,
  title,
  type = "button",
  disabled = false,
  onClick,
  style,
}: WideButtonProps) {
  return (
    <button
      disabled={loading || disabled}
      type={type}
      onClick={onClick}
      className={`flex justify-center items-center w-full shadow-sm shadow-black border-2 text-white font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform backdrop-blur-sm
        ${disabled ? "bg-darken border-gray-700 hover:bg-bg-darken hover:border-gray-700" : "hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent "} 
        ${loading ? "py-2.5" : "py-2"}
        ${style} `}
    >
      {loading ? <LoadingSpinner color="light-gray" /> : title}
    </button>
  );
}
