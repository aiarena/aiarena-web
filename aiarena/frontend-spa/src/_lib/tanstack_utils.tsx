import { SortingState } from "@tanstack/react-table";

export function parseSort(
  sortingMap: Record<string, string>,
  sorting: SortingState
) {
  let sortField = "";
  let sortPrefix = "";
  let sortString = "";

  if (!sorting || !sorting[0] || !sorting[0].id) {
    sortField = "";
    sortPrefix = "";
  } else {
    sortField = sortingMap[sorting[0].id];
    sortPrefix = sorting[0].desc ? "-" : "";
    sortString = sortPrefix + sortField;
  }
  return sortString;
}

export const withAtag = (label: string, href: string, aria: string) => (
  <a
    className="pl-2 hidden md:flex text-left font-semibold text-gray-200 truncate focus:outline-none focus:ring-2 focus:ring-customGreen focus:ring-opacity-50"
    href={href}
    role="cell"
    aria-label={aria}
    title={`${label}`}
  >
    {label}
  </a>
);

export const withClickable = (label: string, onClick: () => void) => (
  <div className="cursor-pointer text-customGreen" onClick={onClick}>
    {label}
  </div>
);
