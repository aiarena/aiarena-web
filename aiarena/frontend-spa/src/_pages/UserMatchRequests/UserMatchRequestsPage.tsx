import { Suspense } from "react";
import UserMatchRequests from "./UserMatchRequests";
import DisplaySkeletonRequestMatches from "@/_components/_display/_skeletons/DisplaySkeletonRequestMatches";

export default function UserMatchRequestsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonRequestMatches />}>
      <UserMatchRequests />
    </Suspense>
  );
}
