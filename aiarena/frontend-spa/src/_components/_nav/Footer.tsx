import React from "react";
import { footerLinks } from "@/_data/footerLinks";
import SocialComponent from "./_footer_parts/SocialNavItem";
import SupportersComponent from "./_footer_parts/Supporters";
import SectionDivider from "../_display/SectionDivider";
import { graphql, useLazyLoadQuery } from "react-relay";
import { FooterQuery } from "./__generated__/FooterQuery.graphql";
import SquareButton from "../_props/SquareButton";
import { getFeatureFlags } from "@/_data/featureFlags";

const Footer: React.FC = () => {
  const data = useLazyLoadQuery<FooterQuery>(
    graphql`
      query FooterQuery {
        stats {
          ...SupportersComponent_stats
        }
      }
    `,
    {}
  );

  // TODO
  // remove undefined and null checks inside the supporters Component, this should all be handled by relay

  return (
    <footer className=" text-white ">
      <SectionDivider />
      <div className="pt-12 container mx-auto px-4 flex flex-col md:flex-row md:flex-wrap justify-between items-start">
        {/* <ServicesComponent services={footerLinks.services} /> */}

        <SupportersComponent stats={data.stats} />
        <SocialComponent links={footerLinks.socialLinks} />
      </div>

      {getFeatureFlags().examples && (
        <SquareButton href="examples" text="UI Examples" />
      )}
      <footer className="p-4 bg-[linear-gradient(90deg,rgba(134,194,50,1)_0%,rgba(50,120,30,1)_100%)] text-center">
        © {new Date().getFullYear()} AI Arena. All rights reserved.
      </footer>
    </footer>
  );
};

export default Footer;
