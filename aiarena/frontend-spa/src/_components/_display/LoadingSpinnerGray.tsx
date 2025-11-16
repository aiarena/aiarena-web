import clsx from "clsx";

interface LoadingSpinnerProps {
  color?: "gray" | "light-gray" | "white" | "black";
  height?: string;
  width?: string;
  thickness?: number;
}

export default function LoadingSpinner({
  color = "gray",
  height = "h-5",
  width = "w-5",
  thickness = 2,
}: LoadingSpinnerProps) {
  return (
    <div
      className={clsx(
        "animate-spin",
        height,
        width,
        `border-${thickness}`,
        "border-t-transparent",
        "rounded-full",
        color === "gray" && "border-gray-600",
        color === "light-gray" && "border-gray-400",
        color === "white" && "border-white",
        color === "black" && "border-black"
      )}
    />
  );
}
