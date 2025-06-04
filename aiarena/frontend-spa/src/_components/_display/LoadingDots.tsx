interface DotsProps {
  offset: number;
}
const Dot = (props: DotsProps) => {
  return (
    <>
      <style>
        {`
          @keyframes sine-wave {
            0%, 100% { 
              opacity: 0;
            }
            50% { 
              opacity: 1;
            }
          }
        `}
      </style>
      <span
        className="bg-customGreen mx-1"
        style={{
          width: "10px",
          height: "10px",
          borderRadius: "50%",
          display: "inline-block",
          opacity: 0,
          animation: `sine-wave 3s ease-in-out infinite ${props.offset}s`,
        }}
      ></span>
    </>
  );
};

export default function LoadingDots({
  dotCount = 5,
  className,
}: {
  dotCount?: number;
  className?: string;
}) {
  const dots = Array.from({ length: dotCount }).map((_, i) => (
    <Dot key={i} offset={i / 3} />
  ));

  return <div className={`flex justify-center ${className}`}>{dots}</div>;
}
