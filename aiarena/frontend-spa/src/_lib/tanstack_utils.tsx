import { SortingState } from "@tanstack/react-table";
import { Link } from "react-router";

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

export const withAtag = (
  label: string,
  href: string,
  aria: string,
  children?: React.ReactNode,
  appendOnEnd?: React.ReactNode
) => (
  <span className="flex justify-between">
    <Link
      className="font-semibold text-gray-200 truncate mr-2"
      to={href}
      role="cell"
      aria-label={aria}
      title={`${label}`}
    >
      {children ? children : label}
    </Link>
    {appendOnEnd && appendOnEnd}
  </span>
);

export const withClickable = (label: string, onClick: () => void) => (
  <div className="cursor-pointer text-customGreen" onClick={onClick}>
    {label}
  </div>
);
