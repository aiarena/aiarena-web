import React, { useState } from "react";

const TestimonialsCarousel: React.FC<{ testimonials: string[] }> = ({ testimonials }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextTestimonial = () => {
    setCurrentIndex((currentIndex + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((currentIndex - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <div className="relative text-center p-4 bg-gray-200 rounded-lg">
      <p className="text-lg italic mb-4">{testimonials[currentIndex]}</p>
      <div className="flex justify-between">
        <button onClick={prevTestimonial} className="bg-gray-400 p-2 rounded-full">
          {"<"}
        </button>
        <button onClick={nextTestimonial} className="bg-gray-400 p-2 rounded-full">
          {">"}
        </button>
      </div>
    </div>
  );
};

export default TestimonialsCarousel;
