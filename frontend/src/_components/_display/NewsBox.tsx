import React from "react";

interface NewsBoxProps {
  title: string;
  date: string;
  content: string;
  videoUrl?: string;
}

const NewsBox: React.FC<NewsBoxProps> = ({ title, date, content, videoUrl }) => {
  const isYouTubeLink = videoUrl?.includes("youtube.com") || videoUrl?.includes("youtu.be");

  return (
      <div className="h-full min-h-full flex flex-col justify-between">
          <div className="flex items-center justify-center relative mb-4">
              <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
              <h3 className="text-lg font-bold text-center px-4"> {date} - {title}</h3>
              <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
          </div>
          <div className="mb-4">
              <p className="text-sm break-words">
                  {content.length > 200 ? content.slice(0, 200) + '...' : content}
              </p>
          </div>
          {/* Video Content */}
          <div className="flex-grow w-full h-full">
              {videoUrl && (
                  isYouTubeLink ? (
                      <iframe
                          className="w-full h-full"
                          src={videoUrl}
                          frameBorder="0"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                      ></iframe>
                  ) : (
                      <video className="w-full h-full" controls>
                          <source src={videoUrl} type="video/mp4"/>
                          Your browser does not support the video tag.
                      </video>
                  )
              )}
          </div>


      </div>


  );
};

export default NewsBox;
