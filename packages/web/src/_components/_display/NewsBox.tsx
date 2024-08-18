import React from "react";

interface NewsBoxProps {
  title: string;
  date: string;
  content: string;
  videoUrl?: string;
}

const NewsBox: React.FC<NewsBoxProps> = ({ title, date, content, videoUrl }) => {
  return (
    <div className="w-full p-4 border rounded-lg ">
  <div className="flex items-center justify-center relative">
       <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
     
    <h3 className="text-lg font-bold mb-2 text-center px-4">News</h3>
    <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
  </div>

      <p className="text-sm mb-4"> {date} - {title}</p>
      <p className="mb-4">{content}</p>
      {videoUrl && (
        <video className="w-full h-auto" controls>
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
};

export default NewsBox;
