import { Suspense } from "react";
import Bot from "./Bot";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export type StatsModalStatus = {
  status: boolean;
  botId: string | undefined;
  competitionName: string | undefined;
  botName: string | undefined;
};

export default function BotPage() {
  return (
    <>
      <Suspense
        fallback={
          <>
            <div className="max-w-7xl mx-auto grid gap-8">
              <div>
                <h4 className="mb-4">Bot information</h4>
                <DisplaySkeleton height={600} styles={SkeletonCardShadow} />
              </div>
              <div>
                <h4 className="mb-4">Competition Participations</h4>
                <DisplaySkeletonTable columns={7} rows={4} />
              </div>
            </div>
            <div>
              <h4 className="mb-4 mt-8">Results</h4>
              <DisplaySkeletonTable columns={12} rows={15} />
            </div>
          </>
        }
      >
        <ErrorBoundaryWrapper componentName="bot">
          <Bot />
        </ErrorBoundaryWrapper>
      </Suspense>
    </>
  );
}
