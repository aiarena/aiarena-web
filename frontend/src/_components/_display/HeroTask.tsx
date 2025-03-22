import Image from "next/image";
import React from "react";
import MainButton from "../_props/MainButton";
import { ImageOverlayWrapper } from "./ImageOverlayWrapper";
import { StringMappingType } from "typescript";

interface HeroTaskProps {
  backgroundImage: string;
  title: string;
  description: string;
  buttonText: string;
  buttonUrl: string;
  alt: string;
}

const HeroTask: React.FC<HeroTaskProps> = ({
  backgroundImage,
  title,
  description,
  buttonText,
  buttonUrl,
  alt,
}) => {
  return (
    <div className="shadow shadow-black block items-start bg-customBackgroundColor1 text-white mb-6 transition-transform transform border border-gray-900 max-w-[30em] min-h-[20em] rounded-lg">
      <div className="relative w-full max-w-[479px] h-[150px] bg-black overflow-hidden border border-gray-600 rounded-t-lg">
        {/* Background Image */}
        <Image
          src={backgroundImage}
          alt={alt}
          fill // Use the fill property for dynamic sizing
          sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 479px"
          style={{
            objectFit: "cover", // Ensure the image fully covers the container
            objectPosition: "center", // Center the image
          }}
          className="absolute inset-0 z-0"
        />

        {/* Overlay */}
        <div className="absolute inset-0 bg-black opacity-10 z-10"></div>

        {/* Optional Content */}
        <div className="relative z-20 flex items-center justify-center h-full"></div>
      </div>

      <div className="flex-grow pt-4">
        <h3 className="text-xl font-bold mb-2 text-customGreen">{title}</h3>
        <p className="text-base  px-6">{description}</p>
        <div className="space-x-4 p-6 mb-auto">
          <MainButton href={buttonUrl} text={buttonText} />
        </div>
      </div>
    </div>
  );
};

export default HeroTask;
