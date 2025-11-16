import clsx from "clsx";

export default function WrappedTitle({
  title,
  font = "font-gugi font-light",
}: {
  title: string;
  font?: string;
}) {
  return (
    <>
      <div className="flex items-center mb-4 justify-center relative">
        <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
        <h2 className={clsx("text-2xl p-2", font)}>{title}</h2>
        <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
    </>
  );
}
