import { flexRender, Table } from "@tanstack/react-table";
import { ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/outline";
import { ReactNode, Suspense, useLayoutEffect, useRef } from "react";
import clsx from "clsx";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import TableSettings from "./TableSettings";
import Divider from "../_display/Divider";

interface TableContainerProps<T> {
  table: Table<T>;
  className?: string;
  loading: boolean;
  appendHeader?: ReactNode;
  appendLeftHeader?: ReactNode;
  minHeight?: number;
}

// division header row type guard and type
type DivisionHeaderRowShape = {
  __kind: "divisionHeader";
  divisionNum: number | null | undefined;
};
function isDivisionHeaderRow<T>(row: T): row is T & DivisionHeaderRowShape {
  if (typeof row !== "object" || row === null) return false;
  if (!("__kind" in row)) return false;

  const candidate = row as { __kind?: unknown };

  return candidate.__kind === "divisionHeader";
}

export function TableContainer<T>({
  table,
  className,
  loading,
  appendHeader,
  appendLeftHeader,
  minHeight = 80,
}: TableContainerProps<T>) {
  const allColumns = table.getAllLeafColumns();

  const visibleColumnCount = allColumns.filter((column) =>
    column.getIsVisible(),
  ).length;

  // We flip the scroll on the table 180 degrees to put the scrollbar at the top on mobile
  // we have to init the component with max right scroll to put the scroll visually max left
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const snapToVisualLeft = () => {
      // rotated 180 = scroll max right = visualy max left
      el.scrollLeft = el.scrollWidth;
    };

    snapToVisualLeft();
    requestAnimationFrame(snapToVisualLeft);
    setTimeout(snapToVisualLeft, 50);
  }, []);
  //

  return (
    <div className={clsx(className)}>
      {/* Table */}

      <div
        className={clsx(
          "overflow-x-auto rounded-2xl border border-neutral-800 backdrop-blur-lg bg-darken-2 shadow-lg shadow-black",
          `min-h-[${minHeight}vh]`,
        )}
      >
        <div className="flex justify-between m-2">
          <div className="flex gap-2">
            <TableSettings>
              <div className="text-white ">
                <Divider label="Visible Table Columns" labelPlacement="left" />
                {allColumns.map((column) => (
                  <label
                    key={column.id}
                    className="flex items-start space-x-4 ml-2"
                  >
                    <input
                      type="checkbox"
                      checked={column.getIsVisible()}
                      onChange={
                        visibleColumnCount == 1 && column.getIsVisible()
                          ? undefined
                          : column.getToggleVisibilityHandler()
                      }
                      disabled={!column.getCanHide()}
                      className="accent-customGreen"
                    />
                    <span>
                      {typeof column.columnDef.header === "string"
                        ? column.columnDef.header
                        : column.id}
                    </span>
                  </label>
                ))}
              </div>
            </TableSettings>
            <div className="flex items-center">{appendLeftHeader}</div>
          </div>
          <div className="flex items-center">{appendHeader}</div>
        </div>
        <div
          ref={scrollerRef}
          className="overflow-x-auto rotate-180 scrollbar-black"
        >
          <div className="rotate-180 min-w-max">
            <table className="w-full border-collapse min-w-max">
              <thead className="bg-darken-2 text-white">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        colSpan={header.colSpan}
                        style={{
                          position: "relative",
                          width: header.getSize(),
                        }}
                        className="text-left select-none border-b border-customGreen font-bold text-customGreen flex-nowrap"
                      >
                        <div className="inline-flex items-center gap-1 w-full justify-between h-full">
                          <div
                            className={clsx(
                              "p-3",
                              "inline-flex",
                              "items-center",
                              "gap-1",
                              "w-full",
                              "justify-between",
                              header.column.getCanSort()
                                ? ""
                                : "text-white font-medium",
                              "mr-5",
                              "group",
                              {
                                "cursor-pointer   hover:text-white":
                                  header.column.getCanSort(),
                              },
                            )}
                            {...(header.column.getCanSort() && !loading
                              ? {
                                  onClick:
                                    header.column.getToggleSortingHandler(),
                                }
                              : {})}
                          >
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext(),
                            )}
                            {header.column.getCanSort() && (
                              <>
                                {header.column.getIsSorted() === "asc" ? (
                                  <span>
                                    <ArrowUpIcon className="size-5 group-hover:hidden" />
                                    <ArrowDownIcon className="size-5 hidden group-hover:inline" />
                                  </span>
                                ) : header.column.getIsSorted() === "desc" ? (
                                  <span>
                                    <ArrowDownIcon className="size-5 opacity-100 group-hover:opacity-0" />
                                  </span>
                                ) : (
                                  <ArrowUpIcon className="size-5 opacity-0 group-hover:opacity-100" />
                                )}
                              </>
                            )}
                          </div>
                          {header.column.getCanResize() && (
                            <div
                              onMouseDown={header.getResizeHandler()}
                              onTouchStart={header.getResizeHandler()}
                              className={clsx(
                                "absolute",
                                "right-0",
                                "top-0",
                                "bottom-0",
                                "w-1",
                                "p-2",
                                "border",
                                "border-transparent",
                                "hover:border-r-white",
                                "cursor-col-resize",
                                {
                                  "border-r-white":
                                    header.column.getIsResizing(),
                                  "border-r-neutral-700":
                                    !header.column.getIsResizing(),
                                },
                              )}
                            >
                              <div
                                className={clsx(
                                  "w-[1px]",
                                  "h-full",
                                  header.column.getIsResizing()
                                    ? "bg-white"
                                    : "bg-customGreen",
                                )}
                              ></div>
                            </div>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              {table.getRowModel().rows.length != 0 ? (
                <Suspense fallback={<LoadingSpinner />}>
                  <tbody className={clsx({ "animate-pulse": loading })}>
                    {table.getRowModel().rows.map((row) => {
                      const original = row.original;

                      // Division header row
                      if (isDivisionHeaderRow(original)) {
                        const label =
                          original.divisionNum != null
                            ? original.divisionNum
                            : "--";

                        return (
                          <tr key={row.id}>
                            <td
                              colSpan={visibleColumnCount}
                              className="text-l font-semibold tracking-widest uppercase text-neutral-200 border-y border-neutral-800 py-3 pl-3"
                            >
                              {label == 0 ? (
                                <span>Awaiting entry</span>
                              ) : (
                                <span>Division {label}</span>
                              )}
                            </td>
                          </tr>
                        );
                      }

                      // Normal data row
                      return (
                        <tr
                          key={row.id}
                          className="even:bg-darken-4 odd:bg-darken hover:bg-darken-3 border-b border-gray-700"
                        >
                          {row.getVisibleCells().map((cell) => (
                            <td
                              key={cell.id}
                              style={{ width: cell.column.getSize() }}
                              className="p-3 text-white border-t border-darken-2 md:min-w-0 md:max-w-0"
                            >
                              <div className="w-full md:overflow-hidden md:text-ellipsis md:whitespace-nowrap">
                                {flexRender(
                                  cell.column.columnDef.cell,
                                  cell.getContext(),
                                )}
                              </div>
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </Suspense>
              ) : (
                <tbody>
                  <tr>
                    <td
                      colSpan={visibleColumnCount}
                      style={{ height: `${minHeight}vh` }}
                      className="text-center"
                    >
                      <div className="flex items-center justify-center h-full text-neutral-400">
                        No results
                      </div>
                    </td>
                  </tr>
                </tbody>
              )}
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
