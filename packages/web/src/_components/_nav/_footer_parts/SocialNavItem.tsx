import React from "react";
import FooterNavItem from "./FooterNavItem";
import { FooterLink } from "@/_data/footerLinks";

interface SocialComponentProps {
  links: FooterLink[];
}

const SocialComponent: React.FC<SocialComponentProps> = ({ links }) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
     <div className="flex items-center mb-4 justify-center relative">
          <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
      <h2 className="text-2xl font-bold p-2">Communities</h2>
      <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
      <ul className="space-y-2 flex flex-col items-center">
        {links.map((link) => (
          <FooterNavItem
            key={link.href}
            href={link.href}
            name={link.name}
            icon={link.icon}
            invertIcon={link.invertIcon}
          />
        ))}
      </ul>
    </div>
  );
};

export default SocialComponent;
