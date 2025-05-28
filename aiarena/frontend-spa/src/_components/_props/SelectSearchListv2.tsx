import React, { useState, useEffect, useRef, ChangeEvent } from "react";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import {
  GraphQLTaggedNode,
  PreloadedQuery,
  usePreloadedQuery,
} from "react-relay";
import { RequestMatchModalBot1Query } from "../_sections/_modals/__generated__/RequestMatchModalBot1Query.graphql";

// Define types for our component
interface Data {
  id: string;
  label: string;
}

interface SearchOrSelectValue {
  select: string;
  searchAndDisplay: string;
}

interface SelectSearchProps {
  query: GraphQLTaggedNode;
  dataRef: PreloadedQuery<RequestMatchModalBot1Query>;
  dataPath: string;

  onChangeRefactor: (value: string) => void;
  onSelectRefactor: (value: string) => void;
  //   selectedValue: string;

  searchOrSelect: SearchOrSelectValue;
  onChange: (value: SearchOrSelectValue) => void;
  onSearch: (searchTerm: string) => void;
  maxHeight?: string;
  placeholder?: string;
  className?: string;
}

const SelectSearchListV2: React.FC<SelectSearchProps> = ({
  query,
  dataRef,
  dataPath,

  onChangeRefactor,
  onSelectRefactor,

  searchOrSelect,

  onChange,
  onSearch,
  maxHeight = "medium",
  placeholder = "Search or select...",
  className = "",
}) => {
  function getNestedValue(obj: unknown, path: string): unknown {
    return path.split(".").reduce((acc: unknown, key: string) => {
      if (typeof acc === "object" && acc !== null && key in acc) {
        return (acc as Record<string, unknown>)[key];
      }
      return undefined;
    }, obj);
  }

  const heightClassMap: Record<string, string> = {
    small: "max-h-36",
    medium: "max-h-48",
    large: "max-h-64",
  };
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const [inputFieldValue, setInputFieldValue] = useState<string>("");

  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const [isLoading, setIsLoading] = useState(false);
  const queryResponse = usePreloadedQuery(query, dataRef);

  const data = React.useMemo(() => {
    function getNodesFromPath(response: unknown, path: string): unknown[] {
      const value = getNestedValue(response, path);
      if (Array.isArray(value)) {
        return value.map((e) =>
          typeof e === "object" && e !== null && "node" in e ? e.node : e
        );
      }
      return [];
    }

    const nodes = getNodesFromPath(queryResponse, dataPath);

    return nodes
      .map((item) => {
        if (
          typeof item === "object" &&
          item !== null &&
          "id" in item &&
          "name" in item
        ) {
          return {
            id: item.id,
            label: item.name,
          };
        }
        return null;
      })
      .filter(Boolean) as Data[];
  }, [queryResponse, dataPath]);

  useEffect(() => {
    if (searchOrSelect?.searchAndDisplay) {
      setInputFieldValue(searchOrSelect.searchAndDisplay);
    } else if (searchOrSelect?.select) {
      const selectedOption = data.find(
        (opt) => opt.id === searchOrSelect.select
      );
      if (selectedOption) {
        setInputFieldValue(selectedOption.label);
      }
    }
  }, [searchOrSelect, data]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (data) {
      setIsLoading(false);
    }
  }, [data]);

  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;

    setInputFieldValue(value);
    setIsLoading(true);

    // Call onChange immediately for UI update
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Set new timeout for onChangeReborn
    debounceTimeoutRef.current = setTimeout(() => {
      onChangeRefactor(value);
    }, 1000);

    onChange({ select: "", searchAndDisplay: value });

    // Call onSearch to trigger loading state and start the search process
    onSearch(value);

    // Open dropdown if it's not already open
    if (!isOpen) {
      setIsOpen(true);
    }
  };

  const handleOptionSelect = (option: Data) => {
    setInputFieldValue(option.label);
    onSelectRefactor(option.id);
    // onChange({ select: option.id, searchAndDisplay: option.label });
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const toggleDropdown = (): void => {
    setIsOpen(!isOpen);
  };

  return (
    <div
      className={`relative w-full text-gray-300 ${className}`}
      ref={dropdownRef}
    >
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          className="w-full px-4 py-2 text-left"
          placeholder={placeholder}
          value={inputFieldValue}
          onChange={handleInputChange}
          onClick={() => setIsOpen(true)}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-0 flex items-center px-2"
          onClick={toggleDropdown}
        >
          {isLoading ? (
            <LoadingSpinner />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-gray-300"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d={
                  isOpen
                    ? "M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"
                    : "M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                }
                clipRule="evenodd"
              />
            </svg>
          )}
        </button>
      </div>

      {isOpen && (
        <div
          className={`absolute z-10 w-full mt-1 bg-neutral-900  border border-gray-600  rounded-md shadow-lg ${heightClassMap[maxHeight]} overflow-auto`}
        >
          {isLoading ? (
            <div className="px-4 py-2  flex items-center">
              <div className="animate-spin h-4 w-4 border-2 border-gray-500 border-t-transparent rounded-full mr-2"></div>
              Loading...
            </div>
          ) : data.length > 0 ? (
            <ul className="py-1 text-left">
              {data.map((option) => (
                <li
                  key={option.id}
                  className="px-4 py-2 cursor-pointer hover:bg-neutral-700"
                  onClick={() => handleOptionSelect(option)}
                >
                  {option.label}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 ">No options found</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SelectSearchListV2;
