import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import UserBots from "./UserBots";

export default function UserBotsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <UserBots />
    </Suspense>
  );
}
