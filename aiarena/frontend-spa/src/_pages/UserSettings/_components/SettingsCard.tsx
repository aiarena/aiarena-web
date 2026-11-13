import React from "react";

interface SettingsCardProps {
  title: string;
  children: React.ReactNode;
}

/** A top-level settings section. Group related controls inside it with
 * `SettingsGroup` so each card reads as one topic with labelled parts. */
export default function SettingsCard({ title, children }: SettingsCardProps) {
  return (
    <section className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
      <h3 className="px-4 py-2 text-base font-semibold border-b border-neutral-600">
        {title}
      </h3>
      <div className="p-4 flex flex-col gap-5 divide-y divide-neutral-700 [&>*:not(:first-child)]:pt-5">
        {children}
      </div>
    </section>
  );
}
