import { Suspense } from "react";
import { Outlet, useParams } from "react-router";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

import WithStatsSideButtons from "@/_components/_nav/WithStatsSideButtons";
import NameCompDisplay from "./NameCompDisplay";

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

      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <NameCompDisplay id={id} />
      </Suspense>
      <WithStatsSideButtons>
        <Outlet />
      </WithStatsSideButtons>
    </section>
  );
}
