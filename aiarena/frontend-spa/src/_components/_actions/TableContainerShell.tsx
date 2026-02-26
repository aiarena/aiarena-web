import { flexRender, Table } from "@tanstack/react-table";
import { ReactNode, Suspense, useLayoutEffect, useRef } from "react";
import clsx from "clsx";
import TbodyLoadingSkeleton from "../_display/_skeletons/TableLoadingSkeleton";
import { ArrowDownIcon, ArrowUpIcon } from "@heroicons/react/24/outline";
import TableSettings from "./TableSettings";
import Divider from "../_display/Divider";

export function TableContainerShell<T>({
  headerTable,
  className,
  appendHeader,
  appendLeftHeader,
  minHeight = 80,
  tbody,
}: {
  headerTable: Table<T>;
  className?: string;
  appendHeader?: ReactNode;
  appendLeftHeader?: ReactNode;
  minHeight?: number;
  tbody: ReactNode;
}) {
  const allColumns = headerTable.getAllLeafColumns();
  const visibleColumnCount = allColumns.filter((c) => c.getIsVisible()).length;

  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const snap = () => (el.scrollLeft = el.scrollWidth);
    snap();
    requestAnimationFrame(snap);
    setTimeout(snap, 50);
  }, []);

  return (
    <div className={clsx(className)}>
      <div
        className={clsx(
          "overflow-x-auto rounded-2xl border border-neutral-800 backdrop-blur-lg bg-darken-2 shadow-lg shadow-black",
          `min-h-[${minHeight}vh]`,
        )}
      >
        <div className="flex justify-between m-2 flex-wrap">
          <div className="flex gap-2">
            <TableSettings>
              <div className="text-white ">
                <Divider label="Visible Table Columns" labelPlacement="left" />
                {allColumns.map((column) => (
                  <label
                    key={column.id}
                    className="flex items-center space-x-4 ml-2"
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
                {headerTable.getHeaderGroups().map((headerGroup) => (
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
                            {...(header.column.getCanSort() && {
                              onClick: header.column.getToggleSortingHandler(),
                            })}
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
              <tbody>
                <Suspense
                  fallback={
                    <TbodyLoadingSkeleton
                      colCount={visibleColumnCount}
                      rowCount={24}
                    />
                  }
                >
                  {tbody}
                </Suspense>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
