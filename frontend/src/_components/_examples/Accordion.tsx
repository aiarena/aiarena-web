import React, { useState } from "react";

const Accordion: React.FC<{ title: string; content: string }> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleAccordion = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="border border-customGreen mb-4 bg-customBackgroundColor1D1 rounded-lg shadow shadow-black">
      <button
        className="w-full text-left p-4 text-lg font-semibold"
        onClick={toggleAccordion}
      >
        {title}
        <span className="float-right">{isOpen ? "-" : "+"}</span>
      </button>
      {isOpen && <div className="p-4 cursor-pointer"  onClick={toggleAccordion}>{content}</div>}
    </div>
  );
};

export default Accordion;
