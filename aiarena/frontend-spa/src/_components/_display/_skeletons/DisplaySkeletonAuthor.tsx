import DisplaySkeleton from "./DisplaySkeleton";

export default function DisplaySkeletonAuthor() {
  return (
    <div className="w-full max-w-[42rem]">
      <div className="relative ">
        <DisplaySkeleton height={120} />
      </div>
    </div>
  );
}
