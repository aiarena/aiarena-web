import clsx from "clsx";
import { ReactNode } from "react";

export default function SocialLinkCard({
  children,
  title,
  iconPath,
  invert,
}: {
  children: ReactNode;
  title: string;
  iconPath: string | undefined;
  invert?: boolean;
}) {
  return (
    <div className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
      <div className="flex justify-between">
        <h3 className="p-4 text-base font-semibold flex">
          {iconPath && (
            <img
              src={iconPath}
              alt={title + "-Icon"}
              width={24}
              height={24}
              className={clsx("mr-2", "w-6", "h-6", invert && "invert")}
            />
          )}
          {title}
        </h3>
        <div className=" p-4">{children}</div>
      </div>
    </div>
  );
}
