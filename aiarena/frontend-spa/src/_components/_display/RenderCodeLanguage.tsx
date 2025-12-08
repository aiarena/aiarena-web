import { BOT_TYPES } from "@/_data/BOT_TYPES";
import pretty from "@/_lib/prettifyCapString";
import clsx from "clsx";

export default function RenderCodeLanguage({
  type: language,
  muted,
}: {
  type: string;
  muted?: boolean;
}) {
  const prettyLang = pretty(language);

  if (language in BOT_TYPES) {
    const obj = BOT_TYPES[language];

    return (
      <span className="flex">
        <img
          src={obj.image}
          alt={obj.name + "-Icon"}
          width={24}
          height={24}
          title={obj.name}
          className={clsx("mr-2")}
        />
        <p className={clsx(muted && "text-gray-400")}>{obj.name}</p>
      </span>
    );
  }

  return <span>{prettyLang}</span>;
}
