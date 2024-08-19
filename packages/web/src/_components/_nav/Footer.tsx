import React from "react";
import { footerLinks } from "@/_data/footerLinks"; 
import SocialComponent from "./_footer_parts/SocialNavItem";
import ServicesComponent from "./_footer_parts/ServicesNavItem";
import SupportersComponent from "./_footer_parts/Supporters";

const Footer: React.FC = () => {
  return (
    <footer className="border-white border-1 bg-fancy-texture text-white py-8">
      <div className="container mx-auto px-4 flex flex-col md:flex-row md:flex-wrap justify-between items-start">
        
        <ServicesComponent services={footerLinks.services} />
        
        <SupportersComponent supporters={footerLinks.topSupporters} />
        
        <SocialComponent links={footerLinks.socialLinks} />
        
      </div>

      <div className="text-center mt-8 text-sm text-gray-400">
        © {new Date().getFullYear()} AI Arena. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
