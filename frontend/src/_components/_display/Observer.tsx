import React, { useEffect, useRef, useState } from "react";

interface ObserverProps {
  children: React.ReactNode;
  threshold?: number; // Trigger visibility based on percentage visible
  className?: string; // Optional class for wrapper styling
  animation?: "fade" | "slideLeft" | "slideUp" | "slideRight"; // Supported animations
}

const Observer: React.FC<ObserverProps> = ({
  children,
  threshold = 0.35,
  className = "",
  animation = "fade", // Default animation
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold },
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [threshold]);

  return (
    <div
      ref={ref}
      className={`${className} ${
        isVisible ? `animate-${animation}` : "opacity-0"
      }`}
    >
      {children}
    </div>
  );
};

export default Observer;
