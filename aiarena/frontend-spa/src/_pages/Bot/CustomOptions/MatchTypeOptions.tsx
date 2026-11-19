export type HardcodedMatchTypeOptions = "REQUESTED" | "COMPETITION";

export const matchTypeOptions: {
  id: HardcodedMatchTypeOptions;
  name: string;
}[] = [
  { id: "REQUESTED", name: "Requested" },
  { id: "COMPETITION", name: "Competition" },
];
