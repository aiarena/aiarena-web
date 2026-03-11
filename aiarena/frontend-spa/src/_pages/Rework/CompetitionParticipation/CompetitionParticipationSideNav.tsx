import { Suspense } from "react";
import { Outlet, useParams } from "react-router";

import WithStatsSideButtons from "@/_components/_nav/WithStatsSideButtons";
import NameCompDisplay from "./NameCompDisplay";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

export default function CompetitionParticipationSideNav() {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Invalid competition participation ID</p>
      </div>
    );
  }

  return (
    <section aria-labelledby="competition-participation-heading">
      <h2 id="competition-participation-heading" className="sr-only">
        Competition Participation Stats
      </h2>

      <Suspense fallback={<DisplaySkeleton height={23} width={500} />}>
        <NameCompDisplay id={id} />
      </Suspense>
      <WithStatsSideButtons>
        <Suspense
          fallback={
            <DisplaySkeleton height={1200} styles={SkeletonCardShadow} />
          }
        >
          <Outlet />
        </Suspense>
      </WithStatsSideButtons>
    </section>
  );
}
