import React from "react";
import FooterNavItem from "./FooterNavItem";
import { FooterLink } from "@/_data/footerLinks";

interface ServicesComponentProps {
  services: FooterLink[];
}

const ServicesComponent: React.FC<ServicesComponentProps> = ({ services }) => {
  return (
    <div className="mb-4 md:mb-0">
      <h4 className="text-lg font-semibold mb-2">Our Services</h4>
      <ul className="space-y-2">
        {services.map((service) => (
          <FooterNavItem key={service.href} href={service.href} name={service.name} />
        ))}
      </ul>
    </div>
  );
};

export default ServicesComponent;
