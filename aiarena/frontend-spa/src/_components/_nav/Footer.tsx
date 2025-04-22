import React from "react";
import { footerLinks } from "@/_data/footerLinks";
import SocialComponent from "./_footer_parts/SocialNavItem";
// import ServicesComponent from "./_footer_parts/ServicesNavItem";
import SupportersComponent from "./_footer_parts/Supporters";
import SectionDivider from "../_display/SectionDivider";
// import SectionDivider from "../_display/SectionDivider";

const Footer: React.FC = () => {
  return (
    <footer className=" text-white ">
      <SectionDivider />
      <div className="pt-12 container mx-auto px-4 flex flex-col md:flex-row md:flex-wrap justify-between items-start">
        {/* <ServicesComponent services={footerLinks.services} /> */}

        <SupportersComponent supporterData={footerLinks.topSupporters} />

        <SocialComponent links={footerLinks.socialLinks} />
      </div>

      <footer className="p-4 bg-[linear-gradient(90deg,rgba(134,194,50,1)_0%,rgba(50,120,30,1)_100%)] text-center">
        © {new Date().getFullYear()} AI Arena. All rights reserved.
      </footer>
    </footer>
  );
};

export default Footer;
