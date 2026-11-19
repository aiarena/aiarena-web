import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";

// Match ID, Bot 1, Bot 2, Map, Started, Assigned to.
const COLUMNS = ["35%", "70%", "70%", "80%", "45%", "55%"];

/** Loading state shaped like the match queue: heading and summary, the filter
 * box, then one section (its heading, e.g. the round name, and its table). */
export default function MatchQueueSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading the match queue">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <DisplaySkeleton height={30} width={190} />
          <DisplaySkeleton height={14} width={260} />
        </div>
        <DisplaySkeleton height={52} width={280} />
      </div>
      {/* Section heading: "Round N · Competition" or "Requested matches" */}
      <div className="mb-3">
        <DisplaySkeleton height={24} width={300} />
      </div>
      <DisplaySkeletonTable columns={COLUMNS} rows={14} />
    </div>
  );
}
