import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import CompetitionsTable from "./CompetitionsTable";
import ActiveCompetitions from "./ActiveCompetitions";
import { CompetitionsQuery } from "./__generated__/CompetitionsQuery.graphql";
import FetchError from "@/_components/_display/FetchError";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function Competitions() {
  const data = useLazyLoadQuery<CompetitionsQuery>(
    graphql`
      query CompetitionsQuery {
        ...ActiveCompetitions
        ...CompetitionsTable
      }
    `,
    {},
  );

  if (!data) {
    return <FetchError type="competitions" />;
  }

  return (
    <>
      <section
        aria-labelledby="competitions-heading"
        className="max-w-7xl mx-auto"
      >
        <h2 id="competition-heading" className="sr-only">
          Competitons
        </h2>

        <div className="grid mb-16">
          <h4 className="mb-4">Active Competitions</h4>
          <Suspense
            fallback={
              <>
                <DisplaySkeleton height={160} styles={SkeletonCardShadow} />
              </>
            }
          >
            <ErrorBoundaryWrapper componentName="active competitions">
              <ActiveCompetitions data={data} />
            </ErrorBoundaryWrapper>
          </Suspense>
        </div>
        <div className="mb-16 ">
          <h4 className="mb-4">Legacy Competitions</h4>
          <Suspense
            fallback={
              <DisplaySkeleton height={600} styles={SkeletonCardShadow} />
            }
          >
            <ErrorBoundaryWrapper componentName="legacy competitions">
              <CompetitionsTable data={data} />
            </ErrorBoundaryWrapper>
          </Suspense>
        </div>
      </section>
    </>
  );
}
