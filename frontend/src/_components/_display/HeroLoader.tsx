import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import React, { useEffect, useState } from "react";

const HeroLoader = ({ onLoadingComplete }: { onLoadingComplete: () => void }) => {
  const [fadeOut, setFadeOut] = useState(false);
  const [contentVisible, setContentVisible] = useState(false);
  const [shouldAnimate, setShouldAnimate] = useState(false);

  useEffect(() => {
    const imageUrls = [
      `${getPublicPrefix()}/generated_assets/dall_e_bg_2.webp`,
      `${getPublicPrefix()}/demo_assets/demo-news.webp`,
    ];

    const checkCache = async () => {
      let uncachedImages = false;

      const promises = imageUrls.map(
        (url) =>
          new Promise<void>((resolve) => {
            const img = new Image();
            img.src = url;

            if (img.complete) {
              console.log(`Cached: ${url}`);
              resolve();
            } else {
              img.onload = () => {
                console.log(`Loaded (was not cached): ${url}`);
                resolve();
              };
              img.onerror = () => {
                console.error(`Failed to load: ${url}`);
                resolve(); // Resolve even if there's an error
              };
              uncachedImages = true;
            }
          })
      );

      await Promise.all(promises);

      if (uncachedImages) {
        setShouldAnimate(true);
      } else {
        setFadeOut(true);
        setTimeout(() => {
          setContentVisible(true);
          onLoadingComplete();
        }, 200); // Skip animation
      }
    };

    checkCache();
  }, [onLoadingComplete]);

  useEffect(() => {
    if (shouldAnimate) {
      const timer = setTimeout(() => {
        setFadeOut(true);
        setTimeout(() => {
          setContentVisible(true);
          onLoadingComplete();
        }, 2000); // Match fade-out duration
      }, 3000); // Simulate loading duration

      return () => clearTimeout(timer);
    }
  }, [shouldAnimate, onLoadingComplete]);

  if (contentVisible) {
    return null; // Skip rendering HeroLoader if animation is complete
  }

  return (
    <div
      className={`fixed inset-0 overflow-y-auto ${
        fadeOut ? "opacity-0 pointer-events-none" : "opacity-100"
      } transition-opacity duration-1000`}
      style={{
        zIndex: 50, // Ensure it’s above other content
      }}
    >
      <div className="absolute inset-0 bg-gray-800 opacity-100"></div>
      <div className="relative flex items-center justify-center min-h-screen">
        <div className="relative w-[300px] h-[300px] flex items-center justify-center">
          <h1 className="text-white text-4xl">Loading...</h1>
        </div>
      </div>
    </div>
  );
};

export default HeroLoader;
