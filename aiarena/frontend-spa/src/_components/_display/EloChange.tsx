export default function EloChange({
  delta,
}: {
  delta: number | null | undefined;
}) {
  if (delta == null) {
    return <span></span>;
  }

  if (delta > 0) {
    return <span style={{ color: "rgb(0,255,0)" }}>+{delta}</span>;
  }
  if (delta < 0) {
    return <span className="text-red-400">{delta}</span>;
  } else {
    return <span>{delta}</span>;
  }
}
