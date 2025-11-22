import {
  ArrowRightIcon,
  ArrowTrendingDownIcon,
  ArrowTrendingUpIcon,
} from "@heroicons/react/24/outline";

export default function EloTrendIcon({
  trend,
}: {
  trend: number | null | undefined;
}) {
  if (trend) {
    return (
      <span>
        {trend >= 15 ? (
          <ArrowTrendingUpIcon
            height={22}
            width={22}
            className="text-customGreen"
          />
        ) : trend <= -15 ? (
          <ArrowTrendingDownIcon
            height={22}
            width={22}
            className="text-red-400"
          />
        ) : (
          <ArrowRightIcon height={22} width={22} />
        )}
      </span>
    );
  } else {
    return (
      <span>
        <ArrowRightIcon height={22} width={22} />
      </span>
    );
  }
}
