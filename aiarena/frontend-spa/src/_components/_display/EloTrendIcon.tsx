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
  console.log(trend);
  if (trend) {
    return (
      <span>
        {trend >= 15 ? (
          <ArrowTrendingUpIcon height={22} width={22} />
        ) : trend <= -15 ? (
          <ArrowTrendingDownIcon height={22} width={22} />
        ) : (
          <ArrowRightIcon height={22} width={22} />
        )}
      </span>
    );
  } else {
    return <span />;
  }
}
