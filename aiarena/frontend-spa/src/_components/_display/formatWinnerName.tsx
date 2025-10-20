export const formatWinnerName = (
  winnerName: string | undefined,
  participantName: string | undefined,
) => {
  return (
    <div className="flex items-center gap-2">
      {winnerName && participantName === winnerName && (
        <div className="mt-[-4px]">👑</div>
      )}
      <div>{participantName}</div>
    </div>
  );
};
