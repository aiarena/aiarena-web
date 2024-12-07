import React, { useState, useEffect } from "react";
import { flattenDiagnosticMessageText } from "typescript";

interface Filter {
  type: "search" | "dropdown";
  label: string;
  field: string;
  placeholder: string;
}


// WARNING! This is the old interface that enforces the fields, but requires 
// all data to be flat. Nested fields does not work with this one, but its prefered
// interface FilterableListProps<T> {
//   data: (T | null | undefined)[];
//   fields: (keyof T)[];
//   filters: Filter[];
//   renderRow: (item: T, index: number) => React.ReactNode;
//   resultsPerPage?: number;
//   fieldLabels?: { [key in keyof T]?: string }; // Add fieldLabels prop
// }

interface FilterableListProps<T> {
    data: (T | null | undefined)[];
    fields: string[];  // Allow string to support nested fields
    filters: Filter[];
    renderRow: (item: T, index: number) => React.ReactNode;
    resultsPerPage?: number;
    fieldLabels?: { [key: string]: string };  // Also change fieldLabels to accept any string
   
  }

export default function FilterableList<T>({
  data,
  fields,
  filters,
  renderRow,
  resultsPerPage: initialResultsPerPage = 10,
  fieldLabels = {}, // Default to an empty object if no fieldLabels are provided
 
}: FilterableListProps<T>) {
    const [sortField, setSortField] = useState<string>(fields[0]);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [filterStates, setFilterStates] = useState<{ [key: string]: string }>(
    {}
  );
  const [resultsPerPage, setResultsPerPage] = useState<number>(
    initialResultsPerPage
  );
  const [showFilterMenu, setShowFilterMenu] = useState<boolean>(false);
  // Sorting logic

//   OLD TYPES
//   const handleSort = (field: keyof T) => {
//     if (field === sortField) {
//       setSortOrder(sortOrder === "asc" ? "desc" : "asc");
//     } else {
//       setSortField(field);
//       setSortOrder("asc");
//     }
//   };



  // Utility to determine visibility class based on responsive config
  // const getResponsiveClass = (className: string): string => {
  //   return Object.keys(responsive)
  //     .map((bp) =>
  //       responsive[bp].some((field) => `display-${bp}` === className)
  //         ? `${bp}:block`
  //         : `${bp}:hidden`
  //     )
  //     .join(" ");
  // };

  // Sorting logic
  const handleSort = (field: string) => {
    if (field === sortField) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  // Handle changes for both search and dropdown filters dynamically
  const handleFilterChange = (field: string, value: string) => {
    setFilterStates((prevFilters) => ({
      ...prevFilters,
      [field]: value,
    }));
    setCurrentPage(1); // Reset to page 1 on filter change
  };





  

  // Reset pagination to page 1 whenever search or filters change
  //   useEffect(() => {
  //     setCurrentPage(1);
  //   }, [searchTerm, dropdownFilters]);

  // Handle dropdown filter changes
  //   const handleDropdownChange = (field: string, value: string) => {
  //     setDropdownFilters((prevFilters) => ({
  //       ...prevFilters,
  //       [field]: value,
  //     }));
  //   };

  // Apply filtering logic based on all filters
  //   const filteredData = data.filter((item) => {
  //     return filters.every((filter) => {
  //       const filterValue = filterStates[filter.field] || "";
  //       if (filter.type === "search") {
  //         if (filterValue.trim() === "") return true;
  //         const searchRegex = new RegExp(filterValue, "i");
  //         return fields.some((field) => searchRegex.test(String(item[field])));
  //       } else if (filter.type === "dropdown") {
  //         return filterValue
  //           ? String(item[filter.field as keyof T]) === filterValue
  //           : true;
  //       }
  //       return true;
  //     });
  //   });



//   FOR OLD TYPES
//   const filteredData = data.filter((item) => {
//     // Skip if the item is null or undefined
//     if (!item) return false;

//     return filters.every((filter) => {
//       const filterValue = filterStates[filter.field] || "";

//       if (filter.type === "search") {
//         if (filterValue.trim() === "") return true;

//         const searchRegex = new RegExp(filterValue, "i");
//         // Ensure we're safely accessing fields, or return false if undefined
//         return fields.some(
//           (field) => item[field] && searchRegex.test(String(item[field]))
//         );
//       } else if (filter.type === "dropdown") {
//         return filterValue
//           ? String(item[filter.field as keyof T] || "").toLowerCase() ===
//               filterValue.toLowerCase()
//           : true;
//       }
//       return true;
//     });
//   });
const filteredData = data.filter((item) => {
    if (!item) return false;
  
    return filters.every((filter) => {
      const filterValue = filterStates[filter.field] || "";
  
      if (filter.type === "search") {
        if (filterValue.trim() === "") return true;
  
        const searchRegex = new RegExp(filterValue, "i");
        // Use getNestedValue to safely access nested fields
        return fields.some(
          (field) => getNestedValue(item, field) && searchRegex.test(String(getNestedValue(item, field)))
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
  function getNestedValue<T>(obj: T, path: string): any {
    return path.split('.').reduce((acc: any, key: string) => acc && acc[key], obj);
  }
  const sortedData = [...filteredData].sort((a, b) => {
    // Check if either 'a' or 'b' is null or undefined
    if (a === null || a === undefined) return 1; // Treat null or undefined as greater (sorted to end)
    if (b === null || b === undefined) return -1; // Treat null or undefined as greater (sorted to end)

    // Safely access the sortField values using the getNestedValue function
    const valueA = String(
      getNestedValue(a, String(sortField)) || ""
    ).toLowerCase();
    const valueB = String(
      getNestedValue(b, String(sortField)) || ""
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
    currentPage * pageSize
  );
  const totalPages = Math.ceil(filteredData.length / pageSize);

  // Ensure current page is valid
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  const renderPagination = () => {
    const paginationButtons = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      for (let page = 1; page <= totalPages; page++) {
        paginationButtons.push(
          <button
            key={page}
            onClick={() => setCurrentPage(page)}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === page
                ? "bg-customGreen text-white"
                : "bg-gray-700 hover:bg-gray-600 text-white"
            }`}
          >
            {page}
          </button>
        );
      }
    } else {
      // Always display the first page
      if (currentPage > 3) {
        paginationButtons.push(
          <button
            key={1}
            onClick={() => setCurrentPage(1)}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === 1
                ? "bg-customGreen text-white"
                : "bg-gray-700 hover:bg-gray-600 text-white"
            }`}
          >
            1
          </button>
        );
      }

      // Add ellipsis if needed at the start
      if (currentPage > 4) {
        paginationButtons.push(
          <span key="start-ellipsis" className="px-4 py-1 text-white">
            ...
          </span>
        );
      }

      // Determine visible pages
      const visiblePages = [];
      if (currentPage <= 4) {
        // When currentPage is at the beginning, show pages 1 to 5
        for (let page = 1; page <= Math.min(5, totalPages); page++) {
          visiblePages.push(page);
        }
      } else if (currentPage >= totalPages - 2) {
        // When currentPage is near the end, show the last 5 pages
        for (let page = totalPages - 4; page <= totalPages; page++) {
          visiblePages.push(page);
        }
      } else {
        // Show 3 pages around the currentPage
        for (let page = currentPage - 1; page <= currentPage + 1; page++) {
          visiblePages.push(page);
        }
      }

      // Add the visible pages to paginationButtons
      visiblePages.forEach((page) => {
        paginationButtons.push(
          <button
            key={page}
            onClick={() => setCurrentPage(page)}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === page
                ? "bg-customGreen text-white"
                : "bg-gray-700 hover:bg-gray-600 text-white"
            }`}
          >
            {page}
          </button>
        );
      });

      // Add ellipsis if needed at the end
      if (currentPage < totalPages - 3) {
        paginationButtons.push(
          <span key="end-ellipsis" className="px-4 py-1 text-white">
            ...
          </span>
        );
      }

      // Always display the last page
      if (currentPage < totalPages - 2) {
        paginationButtons.push(
          <button
            key={totalPages}
            onClick={() => setCurrentPage(totalPages)}
            className={`px-3 py-1 rounded mx-1 ${
              currentPage === totalPages
                ? "bg-customGreen text-white"
                : "bg-gray-700 hover:bg-gray-600 text-white"
            }`}
          >
            {totalPages}
          </button>
        );
      }

      // Ensure the total number of buttons is always 7
      if (paginationButtons.length > 7) {
        paginationButtons.splice(1, paginationButtons.length - 7);
      } else if (paginationButtons.length < 7 && paginationButtons.length > 5) {
        paginationButtons.splice(
          5,
          0,
          <span key="extra-ellipsis" className="px-4 py-1 text-white">
            ...
          </span>
        );
      }
    }

    return paginationButtons;
  };

  const handleChangePage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(event.target.value);
    if (!isNaN(value) && value >= 1 && value <= totalPages) {
      setCurrentPage(value);
    }
  };

  const handleChangeResultsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = Number(event.target.value);
    if (!isNaN(value) && value >= 1) {
      setResultsPerPage(value);
    }
  };

  return (
    <div className="flex flex-col p-4 bg-gray-900">
      {/* Filter button */}
      <button
        onClick={() => setShowFilterMenu(!showFilterMenu)}
        className="mb-4 bg-customGreen text-white p-2 rounded hover:bg-customGreenDarken1 w-[4em]"
      >
        {showFilterMenu ? "Hide Filters" : "Show Filters"}
      </button>

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
              //   const uniqueValues = Array.from(
              //     new Set(
              //       data.map((item) => String(item[filter.field as keyof T]))
              //     )
              //   );
              const uniqueValues = Array.from(
                new Set(
                  data
                    .map(
                      (item) => item && String(item[filter.field as keyof T])
                    ) // Safely handle nulls
                    .filter((value) => value) // Exclude null or empty values from dropdown
                )
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
                        {/* Ensure no null values */}
                        {value ?? "Unknown"}{" "}
                        {/* Optionally handle display for null values */}
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
      <div    className={`grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  gap-4 text-white mb-4 font-bold`}>
        {fields.map((field, index) => (
          <button
            key={index}
            className="text-left font-bold text-lg text-customGreen hover:text-gray-400"
            onClick={() => handleSort(field)}
          >
            {fieldLabels[field]
              ? fieldLabels[field]?.toUpperCase()
              : String(field).toUpperCase()}
          </button>
        ))}
      </div>

      {/* Data Rows */}
      <div
        className="flex-grow mb-4"
        style={{ minHeight: `${pageSize * 56}px` }}
      >
        <ul className="text-white">
          {paginatedData.map((item, index) =>
            // <li key={index} className="mb-2 h-14">
            //   {renderRow(item, index)}
            // </li>
            item ? (
              <li key={index} className="mb-2 h-14">
                {renderRow(item, index)}
              </li>
            ) : (
              <li key={index} className="mb-2 h-14">
                Invalid Data
              </li> // Handle nulls or invalid data
            )
          )}
          {Array.from({ length: pageSize - paginatedData.length }).map(
            (_, index) => (
              <li key={`empty-${index}`} className="mb-2 h-14"></li>
            )
          )}
        </ul>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-wrap justify-center items-center mt-4 p-4 border-t border-gray-900">
        <button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className={`px-3 py-1 rounded mx-1 ${
            currentPage === 1
              ? "bg-gray-700 text-gray-500 cursor-not-allowed"
              : "bg-customGreen text-white"
          }`}
        >
          {"<"}
        </button>
        <div className="hidden md:block">{renderPagination()}</div>
        <div className="block md:hidden">
          <input
            className="w-12 text-black m-2 text-center"
            type="number"
            min="1"
            value={currentPage}
            onChange={handleChangePage}
          />
        </div>
        <button
          onClick={() =>
            setCurrentPage((prev) => Math.min(prev + 1, totalPages))
          }
          disabled={currentPage === totalPages}
          className={`px-3 py-1 rounded mx-1 ${
            currentPage === totalPages
              ? "bg-gray-700 text-gray-500 cursor-not-allowed"
              : "bg-customGreen text-white"
          }`}
        >
          {">"}
        </button>
      </div>
    </div>
  );
}
