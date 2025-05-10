interface SectionDividerProps {
  title?: string;
  darken?: 1 | 2 | 3 | 9; // Optional prop for darken, with values 1, 2, or 3
  className?: string;
  color?: "customGreen" | "gray";
}

const SectionDivider = ({
  title,
  darken,
  className,
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
    <div className={`relative w-full ${className} `}>
      <div
        className={`absolute left-0 w-full h-[2px] shadow shadow-black ${color == "customGreen" ? "bg-customGreen" : ""} ${color == "gray" ? "bg-slate-700" : ""}  ${bgClass}`}
      ></div>
      {title ? (
        <div className="relative mx-auto max-w-[40em]">
          <div
            className={`clip-path-border-trapezoid  ${color == "customGreen" ? "bg-customGreen" : ""} ${color == "gray" ? "bg-slate-700" : ""}  ${bgClass} px-6 py-3`}
          >
            <div className="clip-path-inner-trapezoid bg-gray-900 px-6 py-2 m-[-8px] text-center break-words">
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
