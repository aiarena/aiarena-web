import React from "react";

interface NewsBoxProps {
  videoUrl: string | null | undefined;
}

const NewsBox: React.FC<NewsBoxProps> = ({ videoUrl }) => {
  return (
    <iframe
      className="m-auto  w-full h-[250px] p-2"
      src={videoUrl?.replace("youtube.com", "youtube-nocookie.com")}
      referrerPolicy="strict-origin-when-cross-origin"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    ></iframe>
  );
};

export default NewsBox;
