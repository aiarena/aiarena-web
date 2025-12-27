import AiArenaLoading from "./AiArenaLoading";

type LoadingMoreItemsProps = {
  loadingMessage?: string;
};

export default function LoadingMoreItems({
  loadingMessage = "Loading More items...",
}: LoadingMoreItemsProps) {
  return (
    <div className="p-4 w-full flex flex-col items-center">
      <AiArenaLoading text={loadingMessage} size={120} />
    </div>
  );
}
