import { CoreMatchParticipationResultCauseChoices } from "@/_pages/Rework/Bot/BotResultsTable/__generated__/BotResultsTbody_bot.graphql";
import { resultCauseOptions } from "@/_pages/Rework/Bot/CustomOptions/ResultCauseOptions";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

export function RenderResultCause({
  cause,
}: {
  cause: CoreMatchParticipationResultCauseChoices | null | undefined | "";
}) {
  if (cause === null || cause === undefined || cause === "") {
    return "";
  }

  const readableResult = resultCauseOptions.find(
    (opt) => opt.id === cause.toUpperCase(),
  );

  if (
    readableResult?.name === "Initialization Failure" ||
    readableResult?.name === "Crash" ||
    readableResult?.name === "Race Mismatch" ||
    readableResult?.name === "Timeout" ||
    readableResult?.name === "Error"
  ) {
    return (
      <>
        <span className="flex gap-2 items-center text-amber-300 ">
          <span>
            <ExclamationTriangleIcon height={20} />
          </span>
          <span>{readableResult?.name}</span>
        </span>
      </>
    );
  }

  return readableResult?.name ?? cause;
}
