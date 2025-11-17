import clsx from "clsx";

interface DotProps {
  offset: number;
}

const Dot = ({ offset }: DotProps) => {
  return (
    <span
      className={clsx("bg-customGreen mx-1 loading-dot")}
      style={{
        animationDelay: `${offset}s`,
      }}
    />
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
    <Dot key={i} offset={i * 0.22} />
  ));

  return (
    <>
      <style>
        {`
          @keyframes loading-dots-fast {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
          }

          .loading-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            opacity: 0;
            animation-name: loading-dots-fast;
            animation-duration: 1.2s;
            animation-timing-function: ease-in-out;
            animation-iteration-count: infinite;
          }
        `}
      </style>

      <div className={clsx("flex justify-center", className)}>{dots}</div>
    </>
  );
}
