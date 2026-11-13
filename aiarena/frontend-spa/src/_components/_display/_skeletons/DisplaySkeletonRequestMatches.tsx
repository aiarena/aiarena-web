import DisplaySkeleton from "./DisplaySkeleton";
import DisplaySkeletonTable from "./DisplaySkeletonTable";

export default function DisplaySkeletonRequestMatches() {
  return (
    <div className="grid gap-4">
      <DisplaySkeleton height={45} />
      {/* Match ID, Bot, Opponent, Map, Result, Duration, Started, Replay, Tags */}
      <DisplaySkeletonTable columns={9} rows={20} />
    </div>
  );
}
