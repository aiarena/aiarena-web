import { Suspense } from "react";
import UserMatchRequests from "./UserMatchRequests";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export default function UserMatchRequestsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <UserMatchRequests />
    </Suspense>
  );
}
