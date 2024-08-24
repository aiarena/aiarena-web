import React, { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

const VideoBanner = ({ source }: { source: string }) => {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Re-initialize the video when the component is mounted or remounted
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play();
    }
  }, []);

  const handleRedirect = (path: string) => {
    router.push(path);
  };

  return (
    <div
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
        autoPlay
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
          opacity: 1, // Initial opacity
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)", // For Webkit browsers
        }}
      />
      <div
        className="absolute inset-0 bg-black pointer-events-none"
        style={{
          zIndex: 1,
          opacity: 0.6,
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
        }}
      ></div>
      <div className="video-overlay absolute inset-0 flex flex-col justify-center items-center text-center text-white px-4">
        <h1 className="text-6xl font-bold mb-8 font-gugi text-customGreen ">
          <Image
            className="mx-auto pb-6"
            src={"/ai-arena-logo.png"}
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

// const VideoComponent = ({ source }: { source: string }) => {
//   const router = useRouter();

//   const handleRedirect = (path: string) => {
//     router.push(path);
//   };
//   return (
//     <div
//       style={{
//         width: "100%",
//         height: "85vh",
//         position: "relative",
//         overflow: "hidden",
//       }}
//     >
//       <video
//         src={source}
//         autoPlay
//         loop
//         muted
//         playsInline
//         style={{
//           width: "100%",
//           height: "100%",
//           objectFit: "cover",
//           position: "absolute",
//           top: 0,
//           left: 0,
//           zIndex: 1,
//           opacity: 1, // Initial opacity
//           maskImage:
//             "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
//           WebkitMaskImage:
//             "linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0) 100%)", // For Webkit browsers
//         }}
//       />
//       {/* Tint overlay with matching fade-out effect */}
//       <div
//         className="absolute inset-0 bg-black pointer-events-none"
//         style={{
//           zIndex: 1,
//           opacity: 0.6,
//           maskImage:
//             "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
//           WebkitMaskImage:
//             "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
//         }}
//       ></div>

//       {/* Overlay content */}
//       <div className="video-overlay absolute inset-0 flex flex-col justify-center items-center text-center text-white px-4">
//         <h1 className="text-6xl font-bold mb-8 font-gugi text-customGreen">
//           {" "}
//           <Image
//             className="mx-auto pb-6"
//             src={"/ai-arena-logo.png"}
//             alt="AI-arena-logo"
//             width={150}
//             height={50}
//           ></Image>{" "}
//           AI Arena
//         </h1>
//         <h2 className="text-2xl mb-8">Welcome to the AI Arena!</h2>
//         <div className="flex flex-wrap justify-around w-80">
//           <button
//             onClick={() => handleRedirect("https://aiarena.net/stream/")}
//             className="
//     hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform "
//           >
//             {/* hover:border-4 hover:border-blue-500 */}
//             Watch
//           </button>
//           <button
//             onClick={() => handleRedirect("/play")}
//             className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform "
//           >
//             Play
//           </button>

         
//         </div>
//       </div>
//     </div>
//   );
// };

// export default VideoComponent;
