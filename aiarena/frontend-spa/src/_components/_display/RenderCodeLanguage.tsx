import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import pretty from "@/_lib/prettifyCapString";
import clsx from "clsx";

const LanguageIcons: Record<string, string> = {
  PYTHON: `${getPublicPrefix()}/programming_language_icons/python.svg`,
  JAVA: `${getPublicPrefix()}/programming_language_icons/java.svg`,
  CPPLINUX: `${getPublicPrefix()}/programming_language_icons/cpp.svg`,
  CPPWIN32: `${getPublicPrefix()}/programming_language_icons/cpp.svg`,
  DOTNETCORE: `${getPublicPrefix()}/programming_language_icons/net.svg`,
  NODEJS: `${getPublicPrefix()}/programming_language_icons/nodejs.svg`,
};

export default function RenderCodeLanguage({
  type: language,
}: {
  type: string;
}) {
  const prettyLang = pretty(language);
  if (language in LanguageIcons) {
    const icon = LanguageIcons[language];

    return (
      <span className="flex">
        <img
          src={icon}
          alt={prettyLang + "-Icon"}
          width={24}
          height={24}
          title={prettyLang}
          className={clsx("mr-2")}
        />
        <p>{prettyLang}</p>
      </span>
    );
  }
  return <span>{prettyLang}</span>;
}
