import React from "react";

const TitleBanner: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  return (
    <div className="relative bg-gradient-to-r from-customGreen to-Transparent bg-[length:200%_100%] animate-gradientShift text-white py-12 px-4 text-center shadow-lg rounded-lg">
      <h1 className="text-4xl font-bold">{title}</h1>
      {subtitle && <p className="text-lg mt-2">{subtitle}</p>}
      <div className="absolute inset-0 bg-black opacity-20 rounded-lg"></div>
    </div>
  );
};

export default TitleBanner;
