import React from "react";

import { footerLinks } from "@/_data/footerLinks"; // Adjust the path as needed
import SocialComponent from "./_footer_parts/SocialNavItem";
import ServicesComponent from "./_footer_parts/ServicesNavItem";
import FollowComponent from "./_footer_parts/FollowNavItem";

const Footer: React.FC = () => {
  return (
    <footer className="bg-[url('/fancy-cushion.png')] bg-repeat bg-[length:25px_25px] text-white py-8 ">
      <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between">
        <SocialComponent links={footerLinks.socialLinks} />
        <ServicesComponent services={footerLinks.services} />
        <FollowComponent icons={footerLinks.followIcons} />
      </div>

      <div className="text-center mt-8 text-sm text-gray-400">
        © {new Date().getFullYear()} AI Arena. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
