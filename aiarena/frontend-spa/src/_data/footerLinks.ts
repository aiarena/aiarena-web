import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { socialLinks } from "./socialLinks";

export interface FooterLink {
  icon: string;
  name: string;
  href: string;
  invertIcon: boolean;
}

export interface FollowIcon {
  icon: string;
  href: string;
}
export interface Supporters {
  name: string;
}

export interface FooterLinks {
  socialLinks: FooterLink[];
  services: FooterLink[];
  followIcons: FollowIcon[];
  topSupporters: Supporters[];
}

export const footerLinks: FooterLinks = {
  socialLinks: [
    {
      icon: `${getPublicPrefix()}/social_icons/discord-icon.svg`,
      name: "Discord",
      href: socialLinks["discord"],
      invertIcon: false,
    },
    {
      icon: `${getPublicPrefix()}/social_icons/patreon-icon.svg`,
      name: "Patreon",
      href: socialLinks["patreon"],
      invertIcon: true,
    },
    {
      icon: `${getPublicPrefix()}/social_icons/github-icon.svg`,
      name: "GitHub",
      href: socialLinks["github"],
      invertIcon: true,
    },
    {
      icon: `${getPublicPrefix()}/social_icons/twitch-tile.svg`,
      name: "Twitch",
      href: socialLinks["twitch"],
      invertIcon: false,
    },
    {
      icon: `${getPublicPrefix()}/social_icons/youtube-icon.svg`,
      name: "Youtube",
      href: socialLinks["youtube"],
      invertIcon: false,
    },
  ],
  services: [
    { icon: "/", name: "Service 1", href: "/service1", invertIcon: false },
    { icon: "/", name: "Service 2", href: "/service2", invertIcon: false },
    { icon: "/", name: "Service 3", href: "/service3", invertIcon: false },
  ],
  followIcons: [
    {
      icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z",
      href: "/facebook",
    },
    {
      icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z",
      href: "/instagram",
    },
    {
      icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z",
      href: "/twitter",
    },
  ],
  topSupporters: [{ name: "Latest Supporter Name" }],
};
