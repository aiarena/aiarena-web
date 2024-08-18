export interface FooterLink {
    name: string;
    href: string;
  }
  
  export interface FollowIcon {
    icon: string;
    href: string;
  }
  
  export interface FooterLinks {
    socialLinks: FooterLink[];
    services: FooterLink[];
    followIcons: FollowIcon[];
  }
  
  export const footerLinks: FooterLinks = {
    socialLinks: [
      { name: "Discord", href: "/discord" },
      { name: "Twitter", href: "/twitter" },
      { name: "GitHub", href: "/github" },
      { name: "LinkedIn", href: "/linkedin" },
      { name: "Contact Us", href: "/contact" }
    ],
    services: [
      { name: "Service 1", href: "/service1" },
      { name: "Service 2", href: "/service2" },
      { name: "Service 3", href: "/service3" }
    ],
    followIcons: [
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/facebook" },
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/instagram" },
      { icon: "M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z", href: "/twitter" }
    ]
  };
  