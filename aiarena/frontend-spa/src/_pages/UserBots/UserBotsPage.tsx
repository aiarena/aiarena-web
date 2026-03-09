import { Suspense } from "react";
import UserBots from "./UserBots";
import DisplaySkeletonUserBots from "@/_components/_display/_skeletons/DisplaySkeletonUserBots";

export default function UserBotsPage() {
  return (
    <Suspense fallback={<DisplaySkeletonUserBots />}>
      <UserBots />
    </Suspense>
  );
}
