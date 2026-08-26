import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";

export default function DownloadMap({
  name,
  downloadLink,
}: {
  name: string;
  downloadLink: string | null | undefined;
}) {
  return (
    <a
      href={`${downloadLink}`}
      className="animate-press flex gap-1 items-center"
    >
      <ArrowDownCircleIcon className="h-[18px] w-[18px] shrink-0" /> {name}
    </a>
  );
}
