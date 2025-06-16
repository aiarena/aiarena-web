import LoadingDots from "./LoadingDots";

type LoadingMoreItemsProps = {
  loadingMessage?: string;
};

export default function LoadingMoreItems({
  loadingMessage = "Loading More items...",
}: LoadingMoreItemsProps) {
  return (
    <div className="p-4">
      <p className="text-gray-300 p-3">
        <i>{loadingMessage}</i>
      </p>
      <LoadingDots />
    </div>
  );
}
