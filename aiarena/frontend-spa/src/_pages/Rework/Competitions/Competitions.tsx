import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

import CompetitionsTable from "./CompetitionsTable";
import ActiveCompetitions from "./ActiveCompetitions";
import { CompetitionsQuery } from "./__generated__/CompetitionsQuery.graphql";

export default function Competitions() {
  const data = useLazyLoadQuery<CompetitionsQuery>(
    graphql`
      query CompetitionsQuery {
        ...ActiveCompetitions
        ...CompetitionsTable
      }
    `,
    {}
  );

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
          <Suspense fallback={<LoadingSpinner color="light-gray" />}>
            <ActiveCompetitions data={data} />
          </Suspense>
        </div>
        <div className="mb-16 ">
          <h4 className="mb-4">Legacy Competitions</h4>
          <Suspense fallback={<LoadingSpinner color="light-gray" />}>
            <CompetitionsTable data={data} />
          </Suspense>
        </div>
      </section>
    </>
  );
}
