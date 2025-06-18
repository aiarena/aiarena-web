import clsx from "clsx";

interface LoadingSpinnerProps {
  color?: "gray" | "light-gray" | "white" | "black";
}

export default function LoadingSpinner({
  color = "gray",
}: LoadingSpinnerProps) {
  return (
    <div
      className={clsx(
        "animate-spin",
        "h-5",
        "w-5",
        "border-2",
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
