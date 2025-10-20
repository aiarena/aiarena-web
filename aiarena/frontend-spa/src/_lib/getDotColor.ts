export const getDotColor = (participation: boolean, status: string) => {
  let dotColor: "green" | "blue" | "yellow" | "gray";
  if (status === "OPEN") {
    dotColor = participation ? "green" : "blue";
  } else if (
    ["CREATED", "FROZEN", "PAUSED", "CLOSING"].includes(status ?? "")
  ) {
    dotColor = "yellow";
  } else if (status === "CLOSED") {
    dotColor = "gray";
  } else {
    dotColor = "gray";
  }
  return dotColor;
};
