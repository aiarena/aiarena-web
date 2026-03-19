import { Suspense } from "react";
import Bot from "./Bot";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

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
                <DisplaySkeleton height={300} styles={SkeletonCardShadow} />
              </div>
            </div>
            <div>
              <h4 className="mb-4 mt-8">Results</h4>
              <DisplaySkeleton height={1200} styles={SkeletonCardShadow} />
            </div>
          </>
        }
      >
        <Bot />
      </Suspense>
    </>
  );
}
