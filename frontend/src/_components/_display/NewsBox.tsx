import React from "react";

interface NewsBoxProps {

  videoUrl?: string;
}

const NewsBox: React.FC<NewsBoxProps> = ({  videoUrl }) => {
  const isYouTubeLink = videoUrl?.includes("youtube.com") || videoUrl?.includes("youtu.be");

  return (
    <div className="w-full p-2">
      {/* Video Section */}
      {videoUrl && (
        isYouTubeLink ? (
          <iframe
          className="w-[80em] h-[20em] md:h-[35em] lg:h-[45em] max-w-full max-h-full"
          src={videoUrl.replace("youtube.com", "youtube-nocookie.com")}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
        ) : (
          <video className="w-[80em] h-[45em] max-w-full max-h-full " controls>
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        )
      )}
    </div>
  );
};

export default NewsBox;
