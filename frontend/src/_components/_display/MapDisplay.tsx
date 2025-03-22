import Image from "next/image";
import { useState } from "react";

interface MapDisplayProps {
  mapName: string;
  imageUrl: string;
}

export default function MapDisplay({ mapName, imageUrl }: MapDisplayProps) {
  const [currentImage, setCurrentImage] = useState(imageUrl);
  const [imageError, setImageError] = useState(false); // Track image load errors

  const handleImageError = () => {
    setImageError(true);
    setCurrentImage("/maps/map_fallback.webp"); // Path to your fallback image
  };

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    if (e.currentTarget.naturalWidth === 0) {
      // Fallback for images with 0 width
      handleImageError();
    }
  };

  return (
    <div className="relative w-full h-[80px]">
      {/* Parent container with fixed height */}
      <div className="relative w-full h-full">
        <Image
          src={currentImage}
          alt={mapName}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="object-contain rounded-lg"
          onLoad={handleImageLoad} // Use onLoad instead of onLoadingComplete
          onError={handleImageError} // Handle image load errors
        />
      </div>
      <div className="relative inset-0 flex items-center justify-center">
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/50 to-transparent"></div>
        {/* Centered Text */}
        <p className="relative text-white text-sm font-bold z-10">{mapName}</p>
      </div>
    </div>
  );
}
