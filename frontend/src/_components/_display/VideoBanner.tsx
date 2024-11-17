import React, { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

const VideoBanner = ({ source }: { source: string }) => {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const videoElement = videoRef.current;

    if (videoElement) {
      const handleCanPlay = () => {
        videoElement.play().catch((error) => {
          console.error("Error playing the video:", error);
        });
      };

      // Ensure the video is loaded
      videoElement.load();

      // Play the video only when it's ready (canplay event)
      videoElement.addEventListener("canplay", handleCanPlay);

      return () => {
        videoElement.removeEventListener("canplay", handleCanPlay);
      };
    }
  }, [source]);

  const handleRedirect = (path: string) => {
    router.push(path);
  };

  return (
    <div
      className="bg-oldBg0"
      style={{
        width: "100%",
        height: "85vh",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <video
        ref={videoRef}
        src={source}
        loop
        muted
        playsInline
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 1,
          opacity: 1,
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
        }}
      />
      <div
        className="absolute inset-0 bg-black pointer-events-none"
        style={{
          zIndex: 1,
          opacity: 0.6,
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 1) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 1) 100%)",
        }}
      ></div>
      <div className="video-overlay absolute inset-0 flex flex-col justify-center items-center text-center text-white px-4">
        <h1 className="text-6xl font-bold mb-8 font-gugi text-customGreen">
          <Image
            className="mx-auto pb-6 invert"
            src={`${process.env.PUBLIC_PREFIX}/assets_logo/ai-arena-logo.svg`}
            alt="AI-arena-logo"
            width={150}
            height={50}
          />
          AI Arena
        </h1>
        <h2 className="text-2xl mb-8">Welcome to the AI Arena!</h2>
        <div className="flex flex-wrap justify-around w-80">
          <button
            onClick={() => handleRedirect("https://aiarena.net/stream/")}
            className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
          >
            Watch
          </button>
          <button
            onClick={() => handleRedirect("/play")}
            className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
          >
            Play
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoBanner;
