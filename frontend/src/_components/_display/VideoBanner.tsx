import React, { useEffect, useRef } from "react";

const VideoBanner = ({
  source,
  children,
}: {
  source: string;
  children: React.ReactNode;
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      // Ensure the video starts playing after being loaded
      videoRef.current.play().catch((error) => {
        console.error("Video play failed:", error);
      });
    }
  }, []);

  return (
    <div
      className="relative bg-oldBg0"
      style={{
        width: "100%",
        minHeight: "85vh", // Ensures at least video height
        position: "relative",
      }}
    >
      {/* Video background with fade-out */}
      <video
        ref={videoRef}
        src={source}
        autoPlay
        loop
        muted
        playsInline
        style={{
          width: "100%",
          height: "85vh", // Limit video height
          objectFit: "cover",
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 1,
          opacity: 1,
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0) 100%)",
        }}
      />

      {/* Dark overlay for the video */}
      <div
        className="absolute inset-0 bg-black opacity-70"
        style={{
          zIndex: 2,
          pointerEvents: "none", // Ensures children remain interactive
        }}
      ></div>

      {/* Content container */}
      <div
        className="relative flex flex-col items-center text-center text-white"
        style={{
          zIndex: 3,
          padding: "2rem 1rem",
        }}
      >
        {children}
      </div>
    </div>
  );
};

export default VideoBanner;
