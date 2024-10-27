import React from "react";

interface VideoPlayerProps {
  src: string;
  poster?: string;
  alt?: string;
  controls?: boolean;
  autoPlay?: boolean;
  loop?: boolean;
  muted?: boolean;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  poster,
  alt,
  controls = true,
  autoPlay = false,
  loop = false,
  muted = false,
}) => {
  return (
    <div className="relative w-full h-auto bg-black rounded-lg overflow-hidden shadow-md">
      <video
        className="w-full h-auto"
        src={src}
        poster={poster}
        controls={controls}
        autoPlay={autoPlay}
        loop={loop}
        muted={muted}
        aria-label={alt}
      >
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default VideoPlayer;
