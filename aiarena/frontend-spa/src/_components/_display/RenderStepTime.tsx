import getRedGreenDynamicColor from "@/_lib/getRedGreenDynamicColor";

export default function StepTime({
  time,
}: {
  time: string | number | null | undefined;
}) {
  const stepTime = Math.floor(Number(time) * 1000);
  const color = getRedGreenDynamicColor({
    value: stepTime,
    rangeMin: 50,
    rangeMax: 0,
  });

  return <span style={{ color }}>{stepTime} ms</span>;
}
