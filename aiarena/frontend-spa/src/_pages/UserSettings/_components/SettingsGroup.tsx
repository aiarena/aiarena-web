import React from "react";

interface SettingsGroupProps {
  title: string;
  children: React.ReactNode;
}

export default function SettingsGroup({ title, children }: SettingsGroupProps) {
  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {title}
      </h4>
      <div className="flex flex-col gap-2">{children}</div>
    </div>
  );
}
