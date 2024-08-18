import React from "react";
import FooterNavItem from "./FooterNavItem";
import { FooterLink } from "@/_data/footerLinks";

interface SocialComponentProps {
  links: FooterLink[];
}

const SocialComponent: React.FC<SocialComponentProps> = ({ links }) => {
  return (
    <div className="mb-4 md:mb-0">
      <h4 className="text-lg font-semibold mb-2">Connect with Us</h4>
      <ul className="space-y-2">
        {links.map((link) => (
          <FooterNavItem key={link.href} href={link.href} name={link.name} />
        ))}
      </ul>
    </div>
  );
};

export default SocialComponent;
