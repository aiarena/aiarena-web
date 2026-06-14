import { reverseUrl } from "@/_lib/reverseUrl";

export const navLinks = [
  {
    title: "Home",
    path: reverseUrl("home"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
  },
  {
    title: "Authors",
    path: reverseUrl("authors"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
  },
  {
    title: "Bots",
    path: reverseUrl("bots"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
  },
  {
    title: "Competitions",
    path: reverseUrl("competitions"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
  },
  {
    title: "Results",
    path: reverseUrl("results"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
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
    title: "Wiki",
    path: reverseUrl("wiki:root"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,

  },
  {
    title: "Developers",
    path: reverseUrl("developers"),
    showLoggedIn: true,
    showLoggedOut: true,
    featureFlag: null,
    react: true,
  },
];

export const navbarTitle = {
  title: "AI Arena",
};
