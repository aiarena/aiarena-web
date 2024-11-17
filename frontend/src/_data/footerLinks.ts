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
      { icon: `${process.env.PUBLIC_PREFIX}/social_icons/discord-icon.svg`, name: "Discord", href: "https://discord.com/invite/Emm5Ztz", invertIcon: false},
      { icon: `${process.env.PUBLIC_PREFIX}/social_icons/patreon-icon.svg`, name: "Patreon", href: "https://www.patreon.com/aiarena" , invertIcon: true},
      { icon: `${process.env.PUBLIC_PREFIX}/social_icons/github-icon.svg`, name: "GitHub", href: "https://github.com/aiarena" , invertIcon: true},
      { icon: `${process.env.PUBLIC_PREFIX}/social_icons/twitch-tile.svg`, name: "Twitch", href: "https://www.twitch.tv/aiarenastream" , invertIcon: false},
      { icon: `${process.env.PUBLIC_PREFIX}/social_icons/youtube-icon.svg`, name: "Youtube", href: "https://www.youtube.com/channel/UCMlH43XHsq1TacKm5n4Wbiw" , invertIcon: false},
     
    ],
    services: [
      { icon: "/", name: "Service 1", href: "/service1" , invertIcon: false},
      { icon: "/", name: "Service 2", href: "/service2" , invertIcon: false},
      { icon: "/", name: "Service 3", href: "/service3" , invertIcon: false}
    ],
    followIcons: [
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/facebook" },
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/instagram" },
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/twitter" }
    
    ],
    topSupporters: [
      {name: "Latest Supporter"},
    ]
  };
  