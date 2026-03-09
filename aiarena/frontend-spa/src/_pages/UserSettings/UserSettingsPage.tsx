import { Suspense } from "react";
import UserSettings from "./UserSettings";
import DisplaySkeletonUserSettings from "@/_components/_display/_skeletons/DisplaySkeletonUserSettings";

export default function UserSettingsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonUserSettings />}>
      <UserSettings />
    </Suspense>
  );
}
