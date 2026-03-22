import { Suspense } from "react";
import UserMatchRequests from "./UserMatchRequests";
import DisplaySkeletonRequestMatches from "@/_components/_display/_skeletons/DisplaySkeletonRequestMatches";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function UserMatchRequestsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonRequestMatches />}>
      <ErrorBoundaryWrapper componentName="user match requests">
        <UserMatchRequests />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
