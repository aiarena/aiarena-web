"use client";
import React, { useState } from "react";
import NewsBox from "./NewsBox"; // Import your NewsBox component

interface LatestNewsProps {
  newsData: {
    id: string;
    created: string;
    title: string | null | undefined;
    text: string;
    ytLink: string | null | undefined;
  }[];
}

const LatestNews: React.FC<LatestNewsProps> = ({ newsData }) => {
  // Initialize state to track the index of the current news item
  const [currentIndex, setCurrentIndex] = useState(0);

  // Function to handle showing the previous news item
  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  // Function to handle showing the next news item
  const handleNext = () => {
    if (currentIndex < newsData.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  // Function to handle jumping to a specific news item by clicking a dot
  const handleDotClick = (index: number) => {
    setCurrentIndex(index);
  };

  const currentNewsItem = newsData[currentIndex];

  return (
    <div className="m-2  my-16 border border-gray-600 bg-customBackgroundColor1 rounded-lg flex flex-col items-center gap-2 px-4 py-4 h-full md:max-w-[90%]">
      <div className="flex w-full justify-center items-center mb-2">
        <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
        <h2 className="font-bold mb-0 text-center px-4">News</h2>
        <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
      <div className="flex items-center justify-center relative mb-4">
        <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
        <h3 className="text-lg font-bold text-center px-4">
          {" "}
          {new Date(currentNewsItem.created).toLocaleDateString("en-GB")} -{" "}
          {currentNewsItem.title}
        </h3>
        <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
      <div className="mb-4">
        <p className="text-sm break-words">
          {currentNewsItem.text.length > 200
            ? currentNewsItem.text.slice(0, 200) + "..."
            : currentNewsItem.text}
        </p>
      </div>
      <div className="flex flex-grow gap-2 w-full h-full items-center justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className={`
            
            hidden lg:block 
            ${
              currentIndex === 0
                ? "bg-gray-400 text-gray-300 border-gray-400 hover:border-4 border-4 "
                : "shadow shadow-black hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white"
            } font-semibold py-2 px-2 rounded-full shadow-lg transition duration-300 ease-in-out transform`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>

        <NewsBox key={currentNewsItem.id} videoUrl={currentNewsItem.ytLink} />

        <button
          onClick={handleNext}
          disabled={currentIndex === newsData.length - 1}
          className={`
           hidden lg:block 
            ${
              currentIndex === newsData.length - 1
                ? "bg-gray-400 text-gray-300 border-gray-400 hover:border-4 border-4 "
                : "shadow shadow-black hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white"
            } font-semibold py-2 px-2 rounded-full shadow-lg transition duration-300 ease-in-out transform`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>

      <div className="flex items-center justify-center mt-4">
        {newsData.map((_, index) => (
          <button
            key={index}
            onClick={() => handleDotClick(index)}
            className={` w-6 h-3 rounded-full mx-1 transition duration-300 ${
              currentIndex === index
                ? "bg-customGreen shadow shadow-black"
                : "bg-gray-400"
            }`}
          ></button>
        ))}
      </div>
    </div>
  );
};

export default LatestNews;
