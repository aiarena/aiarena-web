export default function getRedGreenDynamicColor({
  value,
  rangeMin,
  rangeMax,
}: {
  value: number;
  rangeMin: number;
  rangeMax: number;
}): string {
  if (rangeMin === rangeMax) {
    // degenerate case: avoid division by zero
    return "hsl(60, 100%, 50%)"; // yellow as neutral
  }

  const numericMin = Math.min(rangeMin, rangeMax);
  const numericMax = Math.max(rangeMin, rangeMax);

  const clamped = Math.min(numericMax, Math.max(numericMin, value));

  const t = (clamped - numericMin) / (numericMax - numericMin);

  const isInverted = rangeMax < rangeMin;
  const ratio = isInverted ? 1 - t : t;

  const hue = ratio * 120;

  return `hsl(${hue}, 100%, 50%)`;
}
