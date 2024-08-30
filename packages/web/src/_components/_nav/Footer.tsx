import React from "react";
import { footerLinks } from "@/_data/footerLinks"; 
import SocialComponent from "./_footer_parts/SocialNavItem";
import ServicesComponent from "./_footer_parts/ServicesNavItem";
import SupportersComponent from "./_footer_parts/Supporters";

const Footer: React.FC = () => {
  return (
    <footer className="border-white border-1 bg-oldBg2 text-white pt-8">
      <div className="container mx-auto px-4 flex flex-col md:flex-row md:flex-wrap justify-between items-start">
        
        <ServicesComponent services={footerLinks.services} />
        
        <SupportersComponent supporters={footerLinks.topSupporters} />
        
        <SocialComponent links={footerLinks.socialLinks} />
        
      </div>

      <footer className="p-4 bg-gradient-green1 text-center">
      © {new Date().getFullYear()} AI Arena. All rights reserved.
      </footer>
    </footer>
  );
};

export default Footer;
