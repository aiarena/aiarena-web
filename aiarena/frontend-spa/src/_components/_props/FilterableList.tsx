import React, { useState, useEffect } from "react";
import { ChevronUpIcon, ChevronDownIcon } from "@heroicons/react/20/solid";

interface Filter {
  type: "search" | "dropdown";
  label: string;
  field: string;
  placeholder: string;
}

interface FilterableListProps<T> {
  data: (T | null | undefined)[];
  fields: string[];
  filters: Filter[];
  hideMenu?: boolean;
  renderRow: (item: T, index: number) => React.ReactNode;
  resultsPerPage?: number;
  defaultFieldSort?: number;
  defaultSortOrder?: "asc" | "desc";
  fieldLabels?: { [key: string]: string };
  fieldClasses?: { [key: string]: string };
  classes?: string;
}

export default function FilterableList<T>({
  data,
  fields,
  filters,
  renderRow,
  hideMenu = false,
  resultsPerPage: initialResultsPerPage = 13,
  defaultFieldSort = 0,
  defaultSortOrder = "asc",
  fieldLabels = {},
  fieldClasses = {},
  classes = "p-4",
}: FilterableListProps<T>) {
  const [sortField, setSortField] = useState<string>(fields[defaultFieldSort]);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">(defaultSortOrder);
  const [currentPage, setCurrentPage] = useState(1);
  const [filterStates, setFilterStates] = useState<{ [key: string]: string }>(
    {},
  );
  const [resultsPerPage, setResultsPerPage] = useState<number>(
    initialResultsPerPage,
  );
  const [showFilterMenu, setShowFilterMenu] = useState<boolean>(false);

  // Sorting logic
  const handleSort = (field: string) => {
    if (field === sortField) {
      setSortOrder(sortOrder === "desc" ? "asc" : "desc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
    setCurrentPage(1); // Reset to page 1 on sort change
  };

  // Handle changes for both search and dropdown filters dynamically
  const handleFilterChange = (field: string, value: string) => {
    setFilterStates((prevFilters) => ({
      ...prevFilters,
      [field]: value,
    }));
    setCurrentPage(1); // Reset to page 1 on filter change
  };

  const filteredData = data.filter((item) => {
    if (!item) return false;

    return filters.every((filter) => {
      const filterValue = filterStates[filter.field] || "";

      if (filter.type === "search") {
        if (filterValue.trim() === "") return true;

        const searchRegex = new RegExp(filterValue, "i");
        // Use getNestedValue to safely access nested fields
        return fields.some(
          (field) =>
            getNestedValue(item, field) &&
            searchRegex.test(String(getNestedValue(item, field))),
        );
      } else if (filter.type === "dropdown") {
        return filterValue
          ? String(getNestedValue(item, filter.field) || "").toLowerCase() ===
              filterValue.toLowerCase()
          : true;
      }
      return true;
    });
  });

  // Utility function to access nested fields
  function getNestedValue<T>(obj: T, path: string): unknown {
    return path.split(".").reduce((acc: unknown, key: string) => {
      if (typeof acc === "object" && acc !== null && key in acc) {
        return (acc as Record<string, unknown>)[key];
      }
      return undefined;
    }, obj as unknown);
  }
  const sortedData = [...filteredData].sort((a, b) => {
    // Check if either 'a' or 'b' is null or undefined
    if (a === null || a === undefined) return 1;
    if (b === null || b === undefined) return -1;

    // Safely access the sortField values using the getNestedValue function
    const valueA = String(
      getNestedValue(a, String(sortField)) || "",
    ).toLowerCase();
    const valueB = String(
      getNestedValue(b, String(sortField)) || "",
    ).toLowerCase();

    // Compare the string values based on sortOrder
    if (sortOrder === "asc") {
      return valueA.localeCompare(valueB); // Ascending order
    } else {
      return valueB.localeCompare(valueA); // Descending order
    }
  });

  // Pagination logic
  const pageSize = resultsPerPage;

  const paginatedData = sortedData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );
  const totalPages = Math.ceil(filteredData.length / pageSize);

  // Ensure current page is valid
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  const handleChangePage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(event.target.value);
    if (!isNaN(value) && value >= 1 && value <= totalPages) {
      setCurrentPage(value);
    }
  };

  const handleChangeResultsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const value = Number(event.target.value);
    if (!isNaN(value) && value >= 1) {
      if (data.length >= value) {
        setResultsPerPage(value);
      } else {
        setResultsPerPage(data.length);
      }
    }
  };

  const getClassName = (field: string) => fieldClasses[field] || "";

  return (
    <div
      className={`flex flex-col bg-customBackgroundColor1 h-full ${classes}`}
    >
      {/* Filter button */}
      {!hideMenu ? (
        <button
          onClick={() => setShowFilterMenu(!showFilterMenu)}
          className="shadow shadow-black mb-4 bg-customGreen-dark text-white p-2 rounded hover:bg-customGreenDarken1 w-[8em]"
        >
          {showFilterMenu ? "Hide Filters" : "Show Filters"}
        </button>
      ) : null}
      {/* Filters Menu */}
      {showFilterMenu && (
        <div className="bg-gray-800 p-4 rounded mb-4">
          <div className="mb-4">
            <label className="float-left">Results Per Page</label>
            <input
              type="number"
              value={resultsPerPage}
              onChange={(e) => handleChangeResultsPerPage(e)}
              placeholder="Results per page"
              className="w-full p-3 mb-2 border border-gray-700 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-customGreen bg-gray-800 text-white placeholder-gray-500"
              min={1}
            />
          </div>
          {filters.map((filter, index) => {
            if (filter.type === "search") {
              return (
                <div key={index} className="mb-4">
                  <label className="float-left">{filter.label}</label>
                  <input
                    type="text"
                    value={filterStates[filter.field] || ""}
                    onChange={(e) =>
                      handleFilterChange(filter.field, e.target.value)
                    }
                    placeholder={filter.placeholder}
                    className="w-full p-3 mb-2 border border-gray-700 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-customGreen bg-gray-800 text-white placeholder-gray-500"
                  />
                </div>
              );
            } else if (filter.type === "dropdown") {
              const uniqueValues = Array.from(
                new Set(
                  data
                    .map(
                      (item) => item && String(item[filter.field as keyof T]),
                    )
                    .filter((value) => value),
                ),
              );

              return (
                <div key={index} className="mb-4">
                  <label className="float-left">{filter.label}</label>
                  <select
                    value={filterStates[filter.field] || ""}
                    onChange={(e) =>
                      handleFilterChange(filter.field, e.target.value)
                    }
                    className="w-full p-3 border border-gray-700 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-customGreen bg-gray-800 text-white"
                  >
                    <option value="">{filter.placeholder}</option>
                    {uniqueValues.map((value, index) => (
                      <option key={index} value={value ?? ""}>
                        {" "}
                        {value ?? "Unknown"}{" "}
                      </option>
                    ))}
                  </select>
                </div>
              );
            }
            return null;
          })}
        </div>
      )}

      {/* Sorting Header Fields */}
      <div
        className={`grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))] text-white font-bold`}
      >
        {fields.map((field, index) => (
          <button
            key={index}
            className={`py-2 flex justify-between text-left font-bold text-lg text-customGreen hover:text-white bg-darken-5  border-l border-customGreen hover:border-white pl-2  ${getClassName(
              field,
            )}`}
            onClick={() => handleSort(field)}
          >
            {fieldLabels[field]
              ? fieldLabels[field]?.toUpperCase()
              : String(field).toUpperCase()}
            {field === sortField ? (
              sortOrder === "asc" ? (
                <ChevronUpIcon className="h-6 w-6 mr-2" />
              ) : (
                <ChevronDownIcon className="h-6 w-6 mr-2" />
              )
            ) : null}
          </button>
        ))}
      </div>

      {/* Data Rows */}
      <div
        className="h-full flex-grow mb-4 "
        style={{ minHeight: `${pageSize * 40}px` }}
      >
        <ul className="text-white">
          {paginatedData.map((item, index) =>
            item ? (
              <li
                key={index}
                className={`h-12 py-3 shadow-md border border-transparent  hover:border-b-customGreen ${index % 2 ? "bg-darken-4" : "bg-darken"}`}
              >
                {renderRow(item, index)}
              </li>
            ) : (
              <li key={index} className=" p-2 h-12">
                Invalid Data
              </li> // Handle nulls or invalid data
            ),
          )}
          {Array.from({ length: pageSize - paginatedData.length }).map(
            (_, index) => (
              <li key={`empty-${index}`} className="h-12"></li>
            ),
          )}
        </ul>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-wrap justify-center items-center p-4 gap-y-4">
        <div className="flex">
          <button
            onClick={() => setCurrentPage(() => 1)}
            disabled={currentPage === 1 || totalPages == 0}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === 1
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "shadow shadow-black bg-customGreen-dark text-white"
            }`}
          >
            {"<<"}
          </button>
          <button
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1 || totalPages == 0}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === 1
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "shadow shadow-black bg-customGreen-dark text-white"
            }`}
          >
            {"<"}
          </button>
        </div>
        <div className="block">
          <input
            className="w-12 ml-3 text-center"
            type="number"
            min="1"
            value={currentPage}
            onChange={handleChangePage}
          />
        </div>
        <div className="flex">
          <button
            onClick={() =>
              setCurrentPage((prev) => Math.min(prev + 1, totalPages))
            }
            disabled={currentPage === totalPages || totalPages == 0}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === totalPages
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "shadow shadow-black bg-customGreen-dark text-white"
            }`}
          >
            {">"}
          </button>
          <button
            onClick={() => setCurrentPage(() => totalPages)}
            disabled={currentPage === totalPages || totalPages == 0}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === totalPages
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "shadow shadow-black bg-customGreen-dark text-white"
            }`}
          >
            {">>"}
          </button>
        </div>
      </div>
    </div>
  );
}
