import { useState } from "react";
import clsx from "clsx";
import type { BundledLanguage } from "shiki";

import CodeBlock from "@/_components/_display/CodeBlock";

interface LanguageOption {
  display: string;
  code: string;
  lang: BundledLanguage;
}

interface LanguagePickerProps {
  options: LanguageOption[];
  defaultDisplay?: string;
}

export default function LanguagePicker({
  options,
  defaultDisplay,
}: LanguagePickerProps) {
  const [active, setActive] = useState<string>(
    defaultDisplay ?? options[0].display,
  );
  const current = options.find((o) => o.display === active) ?? options[0];

  const control = (
    <div className="inline-flex rounded overflow-hidden border border-neutral-700 bg-black/40 text-xs">
      {options.map((option) => {
        const isActive = option.display === current.display;
        return (
          <button
            key={option.display}
            type="button"
            onClick={() => setActive(option.display)}
            className={clsx(
              "px-2 py-1 transition-colors leading-none",
              isActive
                ? "bg-customGreen text-black font-semibold"
                : "text-gray-200 hover:bg-black/60",
            )}
          >
            {option.display}
          </button>
        );
      })}
    </div>
  );

  return (
    <CodeBlock code={current.code} lang={current.lang} topRight={control} />
  );
}
