import { Suspense } from "react";

import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import AdminCompetitions from "./AdminCompetitions";

export default function AdminCompetitionsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold text-neutral-100">
          Competition awards
        </h2>

        <p className="mt-1 text-sm text-neutral-400">
          Check and award trophies for configured competitions.
        </p>
      </div>

      <Suspense fallback={<DisplaySkeleton height={558} />}>
        <AdminCompetitions />
      </Suspense>
    </div>
  );
}
