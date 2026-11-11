/**
 * Turn the backend's `HH:MM:SS` game duration into a unit form, dropping
 * leading zero units. Matches no longer run past an hour, but older results
 * can — those keep their hours.
 *
 *   formatGameTime("00:07:32") // "7m 32s"
 *   formatGameTime("00:00:45") // "45s"
 *   formatGameTime("01:02:03") // "1h 2m 3s"
 *
 * Anything not shaped like `HH:MM:SS` is returned unchanged.
 */
export function formatGameTime(gameTime: string): string {
  const match = /^(\d+):(\d{2}):(\d{2})$/.exec(gameTime);
  if (!match) return gameTime;

  const [hours, minutes, seconds] = match.slice(1).map(Number);
  const parts: string[] = [];
  if (hours) parts.push(`${hours}h`);
  if (hours || minutes) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);
  return parts.join(" ");
}
