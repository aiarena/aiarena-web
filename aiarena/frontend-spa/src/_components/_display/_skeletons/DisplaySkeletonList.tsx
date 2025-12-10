import DisplaySkeleton from "./DisplaySkeleton";

export default function DisplaySkeletonList({
  bodyHeight = 1400,
}: {
  titleHeight?: number;
  bodyHeight?: number;
}) {
  return (
    <div>
      <DisplaySkeleton height={bodyHeight} />
    </div>
  );
}
