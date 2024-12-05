import React from "react";

interface ToggleButtonProps {
  text?: string; // Make text optional
  className?: string;
  onClick?: () => void;
}

export default function ToggleButton({
  text,
  className = "", // Provide a default className in case it's undefined
  onClick,
}: ToggleButtonProps): JSX.Element | null {
  const handleClick = () => {
    if (onClick) {
      onClick(); // If onClick prop is passed, execute it
    }
  };

  // Only render the button if `text` is defined and not an empty string
  if (!text) {
    return null; // Return null instead of an empty fragment to avoid rendering anything
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={handleClick}
        className={`relative z-10 hover:border-2 border-2 border-customGreen bg-customGreen hover:border-customGreen text-white font-semibold py-2 px-5 rounded-full shadow-lg transition ease-in-out transform ${className}`}
      >
        {text}
      </button>
    </div>
  );
}
