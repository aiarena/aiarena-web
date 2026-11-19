import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";

// The card is translucent dark, about the default bar colour, so bars on it
// use a lighter tone (as on the profile page's card skeletons).
const ON_CARD = { baseColor: "#33343c", highlightColor: "#3f4049" };

function BotSideSkeleton({ align }: { align: "left" | "right" }) {
  return (
    <div
      className={
        align === "right"
          ? "flex flex-1 flex-col items-end gap-1"
          : "flex flex-1 flex-col gap-1"
      }
    >
      {/* Bot name, Race, Language, then the separated Author row */}
      <DisplaySkeleton height={22} width={150} {...ON_CARD} />
      <DisplaySkeleton height={20} width={100} {...ON_CARD} />
      <DisplaySkeleton height={20} width={120} {...ON_CARD} />
      <div
        className={
          align === "right"
            ? "mt-2 flex w-full flex-col items-end border-t border-neutral-700 pt-2"
            : "mt-2 flex w-full flex-col border-t border-neutral-700 pt-2"
        }
      >
        <DisplaySkeleton height={14} width={110} {...ON_CARD} />
      </div>
    </div>
  );
}

/** Loading placeholder shaped like an assigned-match card: header (match ID,
 * competition/round line, status), the two bots facing each other, and the map line. */
export default function AssignedMatchSkeleton() {
  return (
    <div className="rounded-2xl border border-neutral-800 bg-darken-2 p-4 sm:p-5 shadow-lg shadow-black backdrop-blur-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-col gap-1">
          <DisplaySkeleton height={24} width={170} {...ON_CARD} />
          <DisplaySkeleton height={16} width={200} {...ON_CARD} />
        </div>
        <DisplaySkeleton height={26} width={150} styles={{ borderRadius: 9999 }} {...ON_CARD} />
      </div>
      <div className="flex items-center gap-4">
        <BotSideSkeleton align="left" />
        <DisplaySkeleton height={14} width={20} {...ON_CARD} />
        <BotSideSkeleton align="right" />
      </div>
      <div className="mt-4 border-t border-neutral-700 pt-3">
        <DisplaySkeleton height={14} width={180} {...ON_CARD} />
      </div>
    </div>
  );
}
