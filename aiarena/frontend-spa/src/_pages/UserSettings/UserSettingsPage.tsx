import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import UserSettings from "./UserSettings";

export default function UserSettingsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <UserSettings />
    </Suspense>
  );
}
