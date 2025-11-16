import React from "react";

interface NewsBoxProps {
  videoUrl: string | null | undefined;
}

const NewsBox: React.FC<NewsBoxProps> = ({ videoUrl }) => {
  return (
    <iframe
      className="p-4"
      src={videoUrl?.replace("youtube.com", "youtube-nocookie.com")}
      referrerPolicy="strict-origin-when-cross-origin"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      width={420}
      height={215}
    ></iframe>
  );
};

export default NewsBox;
