"use client";

import LoadingDots from "@/_components/_display/LoadingDots";
import { useBotParticipations } from "@/_components/_hooks/useExperimentalBotClientRender";
import { formatDateISO } from "@/_lib/dateUtils";
import { useEffect, useState } from "react";

interface BotParticipationsProps {
  botId: string;
}

export default function BotParticipations({ botId }: BotParticipationsProps) {
  // State to track if component is mounted (client-side)
  const [isMounted, setIsMounted] = useState(false);

  // Always call the hook to follow React rules
  const participations = useBotParticipations(botId);

  // Set mounted state on client
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Only render the actual content on the client-side
  if (!isMounted) {
    return (
      <div className="pt-12 pb-24 items-center">
        <p>Loading rounds and competition rankings...</p>
        <LoadingDots className={"pt-2"} />
      </div>
    );
  }

  if (!participations) {
    return <div>Error loading participation data</div>;
  }

  return (
    <>
      <h2>Competition Participations</h2>
      {participations.competitionParticipations.length === 0 ? (
        <p>No competition participations found</p>
      ) : (
        <ul>
          {participations.competitionParticipations.map(
            (participation, index) => (
              <li key={index}>
                Competition: {participation.competition.name}, Status:{" "}
                {participation.competition.status}, Division:{" "}
                {participation.divisionNum}, Elo: {participation.elo}
              </li>
            )
          )}
        </ul>
      )}

      <h2>Match Participations</h2>
      {participations.matchParticipations.length === 0 ? (
        <p>No match participations found</p>
      ) : (
        <ul>
          {participations.matchParticipations.map((matchPart) => (
            <li key={matchPart.match.id}>
              Date: {formatDateISO(matchPart.match.started)} Match:{" "}
              {matchPart.match.id}, Status: {matchPart.match.status}, Result:{" "}
              {matchPart.result}, ELO Change: {matchPart.eloChange}, Avg Step
              Time: {matchPart.avgStepTime}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
