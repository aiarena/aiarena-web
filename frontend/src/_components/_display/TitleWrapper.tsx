import React from "react";

export default function TitleWrapper({ title }: { title: string }) {
  return (
    <>
      <div className="flex items-center mb-4 justify-center relative">
        <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
        <h2 className="text-2xl font-bold p-2">{title}</h2>
        <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
    </>
  );
}
