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

export const withAtag = (
  label: string,
  href: string,
  aria: string,
  children?: React.ReactNode
) => (
  <a
    className="font-semibold text-gray-200 truncate"
    href={href}
    role="cell"
    target="_blank"
    aria-label={aria}
    title={`${label}`}
  >
    {children ? children : label}
  </a>
);

export const withClickable = (label: string, onClick: () => void) => (
  <div className="cursor-pointer text-customGreen" onClick={onClick}>
    {label}
  </div>
);
