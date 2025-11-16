import LoadingSpinner from "./LoadingSpinnerGray";

type LoadingMoreItemsProps = {
  loadingMessage?: string;
};

export default function LoadingMoreItems({
  loadingMessage = "Loading More items...",
}: LoadingMoreItemsProps) {
  return (
    <div className="p-4 w-full flex flex-col items-center">
      <LoadingSpinner color="white" height="h-15" width="w-15" thickness={4} />
      <p className="text-gray-300 p-3">
        <i>{loadingMessage}</i>
      </p>
    </div>
  );
}
