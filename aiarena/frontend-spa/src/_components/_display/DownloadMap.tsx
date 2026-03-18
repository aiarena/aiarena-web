import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";

export default function DownloadMap({
  name,
  downloadLink,
}: {
  name: string;
  downloadLink: string | null | undefined;
}) {
  return (
    <a href={`${downloadLink}`} className="flex gap-1 items-center">
      <ArrowDownCircleIcon height={18} /> {name}
    </a>
  );
}
