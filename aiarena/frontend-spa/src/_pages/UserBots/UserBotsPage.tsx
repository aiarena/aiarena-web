import { Suspense } from "react";
import UserBots from "./UserBots";
import DisplaySkeletonUserBots from "@/_components/_display/_skeletons/DisplaySkeletonUserBots";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function UserBotsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonUserBots />}>
      <ErrorBoundaryWrapper componentName="user bots">
        <UserBots />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
