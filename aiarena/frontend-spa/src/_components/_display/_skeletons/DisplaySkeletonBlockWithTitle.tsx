import DisplaySkeleton from "./DisplaySkeleton";

export default function DisplaySkeletonBlockWithTitle({
  titleHeight = 50,
  bodyHeight = 500,
}: {
  titleHeight?: number;
  bodyHeight?: number;
}) {
  return (
    <div>
      <DisplaySkeleton height={titleHeight} />
      <div className="py-2"></div>
      <DisplaySkeleton height={bodyHeight} />
    </div>
  );
}
