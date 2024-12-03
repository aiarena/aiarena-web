import React, { ReactNode } from "react";
import Image from "next/image";
import { StaticImageData } from "next/image";
import SectionDivider from "./SectionDivider";

interface ImageOverlayWrapperProps {
  children: ReactNode;
  imageUrl: string | StaticImageData;
  alt: string;
  sectionDivider?: boolean;
  sectionDividerText?: string;
  sectionDividerDarken?: 1 | 2 | 3 | 9;
  blurAmount?: string; // Optional: Control blur level
  opacityAmount?: string; // Optional: Control opacity level
  paddingY?: string; // Optional: Control Y-axis padding
  sizes?:string;
  priority?: boolean;
}

export const ImageOverlayWrapper: React.FC<ImageOverlayWrapperProps> = ({
  children,
  imageUrl,
  alt,
  sectionDivider,
  sectionDividerText,
  sectionDividerDarken,
  blurAmount = "blur-sm", // Default blur
  opacityAmount = "opacity-70", // Default opacity
  paddingY = "py-16", // Default Y-axis padding
  sizes = "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw",
  priority = false
}) => {
  return (
    <div className="relative h-full w-full bg-black pt-0 mt-0 ">
      {sectionDivider ? (
        <div className="relative z-30">
          <SectionDivider title={sectionDividerText} darken={sectionDividerDarken} />
        </div>
      ) : null}

<div className="absolute inset-0"> {/* Add padding to create space around the image */}
  <Image
    src={imageUrl}
    alt={alt}
    sizes={`${sizes}`}
    fill
    className={` z-0 object-cover ${blurAmount}`} // Removed margin, use padding in parent
    priority = {priority}
  />
</div>

      <div className={`absolute inset-0 bg-black ${opacityAmount} z-10`}></div> {/* Allow dynamic opacity */}

      <div className={`relative z-10 flex items-center justify-center h-full ${paddingY}`}> {/* Dynamic padding */}
        {children}
      </div>
    </div>
  );
};
