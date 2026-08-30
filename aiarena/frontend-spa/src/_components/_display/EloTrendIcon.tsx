import {
  ArrowDownIcon,
  ArrowRightIcon,
  ArrowTrendingDownIcon,
  ArrowTrendingUpIcon,
  ArrowUpIcon,
} from "@heroicons/react/24/outline";

export default function EloTrendIcon({
  trend,
  size = 22,
}: {
  trend: number | null | undefined;
  size?: number;
}) {
  if (trend) {
    return (
      <span>
        {trend >= 30 ? (
          <ArrowUpIcon
            height={size}
            width={size}
            className="text-customGreen"
          />
        ) : trend >= 15 && trend < 30 ? (
          <ArrowTrendingUpIcon
            height={size}
            width={size}
            className="text-customGreen"
          />
        ) : trend <= -15 && trend > -30 ? (
          <ArrowTrendingDownIcon
            height={size}
            width={size}
            className="text-red-400"
          />
        ) : trend <= -30 ? (
          <ArrowDownIcon height={size} width={size} className="text-red-400" />
        ) : (
          <ArrowRightIcon height={size} width={size} />
        )}
      </span>
    );
  } else {
    return (
      <span>
        <ArrowRightIcon height={size} width={size} />
      </span>
    );
  }
}
