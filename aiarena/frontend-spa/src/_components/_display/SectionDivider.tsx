import clsx from "clsx";

interface SectionDividerProps {
  title?: string;
  darken?: 1 | 2 | 3 | 9;
  className?: string;
  color?: "customGreen" | "gray" | "gradient";
  height?: 1 | 2 | 3 | 4;
}

const SectionDivider = ({
  title,
  darken,
  className,
  height = 2,
  color = "customGreen",
}: SectionDividerProps) => {
  const bgClass = {
    1: "brightness-100",
    2: "brightness-95",
    3: "brightness-90",
    5: "brightness-75",
    9: "brightness-50",
  }[darken || 1];

  return (
    <div className={clsx("relative w-full", className)}>
      <div
        className={clsx(
          "absolute left-0 w-full shadow shadow-black",
          height === 1 && "h-[1px]",
          height === 2 && "h-[2px]",
          height === 3 && "h-[3px]",
          height === 4 && "h-[4px]",
          color === "customGreen" && "bg-customGreen",
          color === "gray" && "bg-neutral-700",
          color === "gradient" &&
            "bg-[linear-gradient(100deg,rgb(134,194,50,0.1)_0%,rgb(134,194,50,0.3)_80%)]",
          bgClass,
        )}
      ></div>

      {title ? (
        <div className="relative mx-auto max-w-[40em]">
          <div
            className={clsx(
              "clip-path-border-trapezoid px-6 py-3",
              color === "customGreen" && "bg-customGreen",
              color === "gray" && "bg-slate-700",
              bgClass,
            )}
          >
            <div className="clip-path-inner-trapezoid bg-gray-900 px-6 py-2 m-[-8px] text-center break-words ">
              <h2 className="pt-2 pb-3 text-xl font-semibold text-white">
                {title}
              </h2>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SectionDivider;
