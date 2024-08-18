import React from "react";

interface NewsBoxProps {
  title: string;
  date: string;
  content: string;
  videoUrl?: string;
}

const NewsBox: React.FC<NewsBoxProps> = ({ title, date, content, videoUrl }) => {
  return (
    <div className="w-full p-4 border rounded-lg bg-gray-100">
      <h2 className="text-xl font-bold mb-2">{title}</h2>
      <p className="text-sm text-gray-500 mb-4">{date}</p>
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
