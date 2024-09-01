import React, { useState } from "react";

const Accordion: React.FC<{ title: string; content: string }> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleAccordion = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="border-b mb-4">
      <button
        className="w-full text-left p-4 text-lg font-semibold"
        onClick={toggleAccordion}
      >
        {title}
        <span className="float-right">{isOpen ? "-" : "+"}</span>
      </button>
      {isOpen && <div className="p-4 ">{content}</div>}
    </div>
  );
};

export default Accordion;
