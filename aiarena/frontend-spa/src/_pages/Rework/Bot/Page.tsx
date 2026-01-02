import { Suspense } from "react";
import Bot from "./Bot";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export type StatsModalStatus = {
  status: boolean;
  botId: string | undefined;
  competitionName: string | undefined;
  botName: string | undefined;
};

export default function BotPage() {
  return (
    <>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <Bot />
      </Suspense>
    </>
  );
}
