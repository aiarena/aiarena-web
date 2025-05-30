import React, { useState, useEffect, useRef, ChangeEvent } from "react";

// Define types for our component
interface Option {
  id: string;
  label: string;
}

interface SearchOrSelectValue {
  select: string;
  searchAndDisplay: string;
}

interface SelectSearchProps {
  options: Option[];
  searchOrSelect: SearchOrSelectValue;
  onChange: (value: SearchOrSelectValue) => void;
  onSearch: (searchTerm: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

const SelectSearch: React.FC<SelectSearchProps> = ({
  options,
  searchOrSelect,
  onChange,
  onSearch,
  isLoading = false,
  placeholder = "Search or select...",
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize display value from prop
  useEffect(() => {
    if (searchOrSelect?.searchAndDisplay) {
      setSearchTerm(searchOrSelect.searchAndDisplay);
    } else if (searchOrSelect?.select) {
      const selectedOption = options.find(
        (opt) => opt.id === searchOrSelect.select
      );
      if (selectedOption) {
        setSearchTerm(selectedOption.label);
      }
    }
  }, [searchOrSelect, options]);

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

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);

    // Call onChange immediately for UI update
    onChange({ select: "", searchAndDisplay: value });

    // Call onSearch to trigger loading state and start the search process
    onSearch(value);

    // Open dropdown if it's not already open
    if (!isOpen) {
      setIsOpen(true);
    }
  };

  const handleOptionSelect = (option: Option) => {
    setSearchTerm(option.label);
    onChange({ select: option.id, searchAndDisplay: option.label });
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const toggleDropdown = (): void => {
    setIsOpen(!isOpen);
  };

  return (
    <div
      className={`relative w-full text-black ${className}`}
      ref={dropdownRef}
    >
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder={placeholder}
          value={searchTerm}
          onChange={handleInputChange}
          onClick={() => setIsOpen(true)}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-0 flex items-center px-2"
          onClick={toggleDropdown}
        >
          {isLoading ? (
            <div className="animate-spin h-5 w-5 border-2 border-gray-500 border-t-transparent rounded-full" />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-gray-500"
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
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {isLoading ? (
            <div className="px-4 py-2 text-gray-500 flex items-center">
              <div className="animate-spin h-4 w-4 border-2 border-gray-500 border-t-transparent rounded-full mr-2"></div>
              Loading...
            </div>
          ) : options.length > 0 ? (
            <ul className="py-1 text-left">
              {options.map((option) => (
                <li
                  key={option.id}
                  className="px-4 py-2 cursor-pointer hover:bg-blue-50"
                  onClick={() => handleOptionSelect(option)}
                >
                  {option.label}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 text-gray-500">No options found</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SelectSearch;
