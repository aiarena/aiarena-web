export function parseMatchResult(
  result: string | undefined,
  winner: string | undefined
) {
  if (result == undefined) {
    return "";
  }

  if (result == "MATCHCANCELLED") {
    return "Match Cancelled";
  }
  if (result == "INITIALIZATIONERROR") {
    return "Initialization Error";
  }

  if (result == "PLAYER1WIN" || result == "PLAYER2WIN") {
    if (winner == undefined) {
      return "Winner: Unknown";
    }
    return `Winner: ${winner}`;
  } else {
    return result;
  }
}
