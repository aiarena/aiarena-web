import useNow from "@/_components/_hooks/useNow";
import timeAgoShort from "@/_lib/timeAgoSort";

/** Live time since `since` (e.g. "4m 12s"), updating every second. */
export default function TimeAgo({ since }: { since: string | Date | number }) {
  const now = useNow();
  return <>{timeAgoShort(since, now)}</>;
}
