export const statsSideNavbarLinks = [
  {
    name: "Overview",
    state: "overview",
  },
  {
    name: "Maps",
    state: "maps",
  },
  {
    name: "Opponents",
    state: "matchups",
  },
] as const;

export const statsTopNavbarLinks = [
  {
    parent: "overview",
    name: "ELO Graph",
    state: "elograph",
  },
  {
    parent: "overview",
    name: "Wins By Time",
    state: "winsbytime",
  },
  {
    parent: "overview",
    name: "Wins By Race",
    state: "winsbyrace",
  },
] as const;
