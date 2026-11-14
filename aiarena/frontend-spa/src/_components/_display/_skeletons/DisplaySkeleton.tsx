import { CSSProperties } from "react";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
export default function DisplaySkeleton({
  height = undefined,
  width = undefined,
  count = undefined,
  styles,
  circle,
  baseColor = "#18191E",
  highlightColor = "#22232B",
}: {
  height?: number;
  width?: number;
  count?: number;
  circle?: boolean;
  styles?: CSSProperties;
  /** Override the bar colours, e.g. lighter bars on a lighter surface. */
  baseColor?: string;
  highlightColor?: string;
}) {
  return (
    <SkeletonTheme baseColor={baseColor} highlightColor={highlightColor}>
      <p>
        <Skeleton
          height={height}
          width={width}
          count={count}
          circle={circle}
          style={styles}
          customHighlightBackground="
            linear-gradient(
              90deg,
              var(--base-color) 30%,
              var(--highlight-color) 50%,
              var(--base-color) 70%
            )
          "
        />
      </p>
    </SkeletonTheme>
  );
}
