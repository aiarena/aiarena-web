import { getFeatureFlags } from "./featureFlags";

export const navLinks = [
  {
    title: "Home",
    path: "/",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Wiki",
    path: "/wiki",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Authors",
    path: "/authors",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Bots",
    path: "/bots",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Competitions",
    path: "/competitions",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Match Queue",
    path: "/match-queue",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Result",
    path: "/results",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Live Stream",
    path: "https://www.twitch.tv/aiarenastream",
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Project Finance",
    path: `https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "API",
    path: `/api`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Dashboard",
    path: `/dashboard/`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
  },
  {
    title: "Authors",
    path: `/dashboard/rework/authors`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: getFeatureFlags().reactRework,
  },
  {
    title: "Competitions",
    path: `/dashboard/rework/competitions`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: getFeatureFlags().reactRework,
  },
  {
    title: "Bots",
    path: `/dashboard/rework/bots`,
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: getFeatureFlags().reactRework,
  },
];

export const navbarTitle = {
  title: "AI Arena",
};
