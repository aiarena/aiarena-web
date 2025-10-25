import { flexRender, Table } from "@tanstack/react-table";
import { ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/outline";
import { ReactNode, Suspense } from "react";
import clsx from "clsx";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import TableSettings from "./TableSettings";
import Divider from "../_display/Divider";

interface TableContainerProps<T> {
  table: Table<T>;
  className?: string;
  loading: boolean;
  appendHeader?: ReactNode;
}

export function TableContainer<T>({
  table,
  className,
  loading,
  appendHeader,
}: TableContainerProps<T>) {
  const allColumns = table.getAllLeafColumns();

  const visibleColumnCount = allColumns.filter((column) =>
    column.getIsVisible()
  ).length;

  return (
    <div className={clsx(className)}>
      {/* Table */}

      <div className="overflow-x-auto rounded-2xl border border-neutral-800 backdrop-blur-lg bg-darken-2  min-h-[80vh]">
        <div className="flex justify-between m-2">
          <TableSettings>
            <div className="text-white">
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
          <div className="flex items-center">{appendHeader}</div>
        </div>

        <table className="w-full border-collapse min-w-max">
          <thead className="bg-darken-2 text-white">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    colSpan={header.colSpan}
                    style={{ position: "relative", width: header.getSize() }}
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
                          "cursor-pointer",
                          "mr-5",
                          "group",
                          "hover:text-white"
                        )}
                        {...(header.column.getCanSort() && !loading
                          ? {
                              onClick: header.column.getToggleSortingHandler(),
                            }
                          : {})}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
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
                              "border-r-white": header.column.getIsResizing(),
                              "border-r-neutral-700":
                                !header.column.getIsResizing(),
                            }
                          )}
                        >
                          <div
                            className={clsx(
                              "w-[1px]",
                              "h-full",
                              header.column.getIsResizing()
                                ? "bg-white"
                                : "bg-customGreen"
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
                {table.getRowModel().rows.map((row) => (
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
                            cell.getContext()
                          )}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </Suspense>
          ) : (
            <tbody>
              <tr>
                <td
                  colSpan={visibleColumnCount}
                  className="text-center align-middle h-[30vh]"
                >
                  No results
                </td>
              </tr>
            </tbody>
          )}
        </table>
      </div>
    </div>
  );
}
