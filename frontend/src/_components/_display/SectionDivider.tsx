import React from 'react';

interface SectionDividerProps {
  title?: string;
  darken?: 1 | 2 | 3 | 9; // Optional prop for darken, with values 1, 2, or 3
}

const SectionDivider = ({ title, darken }: SectionDividerProps) => {
  // Determine the background class based on the darken prop
  const bgClass = {
    1: 'bg-customGreenDarken1',
    2: 'bg-customGreenDarken2',
    3: 'bg-customGreenDarken3',
    9: 'bg-customGreenDarken9',
  }[darken || 1]; // Default to bg-customGreenDarken1 if no darken value is provided

  return (
    <div className="relative w-full ">
      {/* Full-width line */}
      <div className={`absolute left-0 w-full h-[2px] ${bgClass}`}></div>

      {title ? (
        <div className="relative mx-auto max-w-[40em]">
          {/* Outer border trapezoid */}
          <div className={`clip-path-border-trapezoid ${bgClass} px-6 py-3`}>
            {/* Inner background trapezoid */}
            <div className="clip-path-inner-trapezoid bg-gray-900 px-6 py-2 m-[-8px] text-center break-words">
              <h2 className="pt-2 pb-3 text-xl font-semibold text-white">{title}</h2>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SectionDivider;
