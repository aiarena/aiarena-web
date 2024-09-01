import React from "react";

const GradientButton: React.FC<{ text: string; onClick: () => void }> = ({
  text,
  onClick,
}) => {
  return (
    <button
      onClick={onClick}
      className="bg-gradient-to-r from-green-400 to-blue-500 text-white py-3 px-8 rounded-full shadow-lg hover:from-blue-500 hover:to-green-400 transition-all duration-300"
    >
      {text}
    </button>
  );
};

export default GradientButton;
