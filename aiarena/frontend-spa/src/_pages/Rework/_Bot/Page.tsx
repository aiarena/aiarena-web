import { Suspense } from "react";
import Bot from "./Bot";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export default function BotPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Bot />
    </Suspense>
  );
}
