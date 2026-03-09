import SectionDivider from "../SectionDivider";
import DisplaySkeleton from "./DisplaySkeleton";

export default function DisplaySkeletonUserSettings() {
  return (
    <>
      <div className="lg:flex lg:flex-row lg:gap-4">
        <div className="mx-auto lg:mx-0 w-60 gap-4 grid">
          <DisplaySkeleton height={240} />
          <DisplaySkeleton height={45} />
          <DisplaySkeleton height={45} />
        </div>
        {/* desktop view statusinfo */}
        <div className="hidden lg:block mt-4">
          <DisplaySkeleton height={45} />
          <DisplaySkeleton height={45} />
          <DisplaySkeleton height={45} />
        </div>
        <div className="hidden lg:block mt-4"></div>

        {/* mainsection */}
        <div className="w-full">
          <div className="lg:block lg:text-left flex justify-center">
            <div className="leading-tight py-4">
              <DisplaySkeleton height={45} />
            </div>
          </div>
          <SectionDivider className="pb-4" />
          <div className="gap-4 flex flex-col max-w-[26em]">
            <DisplaySkeleton height={65} />
            <DisplaySkeleton height={65} />
            <DisplaySkeleton height={45} />
          </div>
        </div>
      </div>
    </>
  );
}
