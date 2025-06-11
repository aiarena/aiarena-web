export function getMatchResultParsed(
  result: string | undefined,
  player1: string | undefined,
  player2: string | undefined
) {
  if (!result) return "";

  const resultOptions: Record<string, string> = {
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
    "": "",
  };

  return resultOptions[result] || "";
}
