import React, { useState } from 'react';
import NewsBox from './NewsBox'; // Import your NewsBox component

const LatestNews = ({ newsData }) => {
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

  const currentNewsItem = newsData[currentIndex];

  return (
    <div className="border border-gray-600 rounded-lg flex flex-col items-center gap-2 px-2 py-4 h-full max-w-[60em]">
      <div className="flex flex-grow gap-2 w-full h-full items-center justify-between">
        {/* Previous Button with SVG Arrow */}
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className={`${
            currentIndex === 0
              ? 'bg-gray-400 text-gray-300 border-gray-400 hover:border-4 border-4 '
              : 'hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white'
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
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        {/* NewsBox */}
        <div className="flex-grow h-[33em]">
          <NewsBox
            key={currentNewsItem.id}
            title={currentNewsItem.title}
            date={new Date(currentNewsItem.created).toLocaleDateString('en-GB')}
            content={currentNewsItem.text}
            videoUrl={currentNewsItem.ytLink}
          />
        </div>

        {/* Next Button with SVG Arrow */}
        <button
          onClick={handleNext}
          disabled={currentIndex === newsData.length - 1}
          className={`${
            currentIndex === newsData.length - 1
              ? 'bg-gray-400 text-gray-300 border-gray-400 hover:border-4 border-4 '
              : 'hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white'
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
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default LatestNews;
