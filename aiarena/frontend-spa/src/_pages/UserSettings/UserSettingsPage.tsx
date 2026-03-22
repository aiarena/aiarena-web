import { Suspense } from "react";
import UserSettings from "./UserSettings";
import DisplaySkeletonUserSettings from "@/_components/_display/_skeletons/DisplaySkeletonUserSettings";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function UserSettingsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonUserSettings />}>
      <ErrorBoundaryWrapper componentName="user settings">
        <UserSettings />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
