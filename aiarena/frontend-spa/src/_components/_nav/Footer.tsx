import React from "react";
import { footerLinks } from "@/_data/footerLinks";
import SocialComponent from "./_footer_parts/SocialNavItem";
import SupportersComponent from "./_footer_parts/Supporters";
import SectionDivider from "../_display/SectionDivider";
import SquareButton from "../_actions/SquareButton";
import { getFeatureFlags } from "@/_data/featureFlags";

const Footer: React.FC = () => {
  return (
    <footer className=" text-white bg-darken">
      <SectionDivider />
      <div className="pt-12 container mx-auto px-4 flex flex-col md:flex-row md:flex-wrap justify-between items-start">
        <SupportersComponent />

        <SocialComponent links={footerLinks.socialLinks} />
      </div>

      {getFeatureFlags().examples && (
        <SquareButton href="examples" text="UI Examples" />
      )}
      <footer className="p-1 bg-[linear-gradient(120deg,rgba(134,194,50,1)_0%,rgba(94,140,30,1)_50%)] text-center">
        © {new Date().getFullYear()} AI Arena. All rights reserved.
      </footer>
    </footer>
  );
};

export default Footer;
