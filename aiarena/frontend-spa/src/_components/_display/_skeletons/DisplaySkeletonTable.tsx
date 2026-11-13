import DisplaySkeleton from "./DisplaySkeleton";

// Bar widths (as a share of each cell) cycled through when only a column count
// is given, so the placeholder doesn't look like a uniform grid.
const DEFAULT_CELL_WIDTHS = ["40%", "75%", "60%", "80%", "50%", "65%"];

interface DisplaySkeletonTableProps {
  /** Number of columns, or the width of each column's bars (e.g. "70%").
   * Match the real table so content replaces it without the layout jumping. */
  columns: number | string[];
  rows?: number;
  /** Show the row above the header where the table settings button sits. */
  toolbar?: boolean;
}

/** Loading placeholder for a big table (one rendered by `TableContainer`):
 * the same card, settings button, header row and alternating rows. */
export default function DisplaySkeletonTable({
  columns,
  rows = 12,
  toolbar = true,
}: DisplaySkeletonTableProps) {
  const cellWidths =
    typeof columns === "number"
      ? Array.from({ length: columns }, (_, i) => DEFAULT_CELL_WIDTHS[i % DEFAULT_CELL_WIDTHS.length])
      : columns;
  const gridStyle = { gridTemplateColumns: `repeat(${cellWidths.length}, minmax(0, 1fr))` };

  return (
    <div
      aria-busy="true"
      aria-label="Loading table"
      // Same card as TableContainer: solid, so the page texture doesn't show
      // through (the row shades below are translucent and sit on top of it).
      className="overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-900 shadow-lg shadow-black"
    >
      {toolbar && (
        <div className="p-2">
          <DisplaySkeleton height={42} width={52} />
        </div>
      )}
      <div
        // Neutral rule, not the real header's green: a green line that appears
        // and then shifts when the table loads draws the eye to the swap.
        className="grid gap-4 border-b border-neutral-700 bg-darken-2 px-3 py-3"
        style={gridStyle}
      >
        {cellWidths.map((_, i) => (
          <div key={i} className="w-1/2">
            <DisplaySkeleton height={18} />
          </div>
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div
          key={r}
          className="grid gap-4 px-3 py-3 odd:bg-darken even:bg-darken-4"
          style={gridStyle}
        >
          {cellWidths.map((width, c) => (
            <div key={c} style={{ width }}>
              <DisplaySkeleton height={18} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
