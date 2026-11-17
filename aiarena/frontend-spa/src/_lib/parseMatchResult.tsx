import { CoreResultTypeChoices } from "@/_pages/UserMatchRequests/__generated__/UserMatchRequestsTable_viewer.graphql";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

export function getMatchResultParsed(
  result: CoreResultTypeChoices | undefined,
  player1: string | undefined,
  player2: string | undefined
) {
  if (!result) return "";

  const resultOptions: Record<CoreResultTypeChoices, string> = {
    MATCHCANCELLED: "Match Cancelled",
    INITIALIZATIONERROR: "Initialization Error",
    ERROR: "Error",
    PLAYER1WIN: `${player1} Win`,
    PLAYER1CRASH: `${player1} Crash`,
    PLAYER1TIMEOUT: `${player1} Timeout`,
    PLAYER1RACEMISMATCH: `${player1} Race Mismatch`,
    PLAYER1SURRENDER: `${player1} Surrender`,
    PLAYER2WIN: `${player2} Win`,
    PLAYER2CRASH: `${player2} Crash`,
    PLAYER2TIMEOUT: `${player2} Timeout`,
    PLAYER2RACEMISMATCH: `${player2} Race Mismatch`,
    PLAYER2SURRENDER: `${player2} Surrender`,
    TIE: "Tie",
  };

  if (
    result === "PLAYER1WIN" ||
    result === "PLAYER2WIN" ||
    result === "TIE" ||
    result === "MATCHCANCELLED"
  ) {
    return <span>{resultOptions[result] || ""}</span>;
  }

  return (
    <>
      <span className="flex gap-2 items-center text-amber-300 ">
        <span>
          <ExclamationTriangleIcon height={20} />
        </span>
        <span>{resultOptions[result]}</span>
      </span>
    </>
  );
}
