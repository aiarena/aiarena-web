import DisplaySkeleton from "./DisplaySkeleton";

export default function TbodyLoadingSkeleton({
  rowCount = 12,
  colCount,
}: {
  rowCount?: number;
  colCount: number;
}) {
  return Array.from({ length: rowCount }).map((_, r) => (
    <tr key={r} className="odd:bg-darken-4 even:bg-darken">
      {Array.from({ length: colCount }).map((__, c) => (
        <td key={c} className="p-3  md:min-w-0 md:max-w-0 ">
          <DisplaySkeleton height={22} />
        </td>
      ))}
    </tr>
  ));
}
