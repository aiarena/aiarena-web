import LoadingDots from "./LoadingDots";

export const PlaceholderLoadingFallback = () => {
  return (
    <div className="pt-12 pb-24 items-center">
      <p>Loading...</p>
      <LoadingDots className={"pt-2"} />
    </div>
  );
};
