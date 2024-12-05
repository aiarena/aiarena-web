"use client"

import WrappedTitle from "@/_components/_display/WrappedTitle";
import Accordion from "@/_components/_examples/Accordion";
import Button from "@/_components/_props/Button";
import MainButton from "@/_components/_props/MainButton";
import Image from "next/image";
import React from "react";
import { FooterLink, footerLinks } from "@/_data/footerLinks";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import SubscriptionList from "@/_components/_display/SubscriptionList";

const AboutUs = () => {
  return (
  <ArticleWrapper>
      {/* AI Arena Overview */}
      <section className="text-center py-12 ">
        <h1 className="text-4xl text-customGreen font-bold mb-8">
          What is AI Arena?
        </h1>
        <p className="text-lg max-w-2xl mx-auto">
          AI Arena is a nonprofit platform where AI bots battle in
          StarCraft 2 matches, streamed live. Our competitive platform offers multiple
          ladders for ranking, in-depth statistics, and live game streams. Join
          us on 
          <a href="https://twitch.tv" className=" pl-1 text-customGreen underline">
            Twitch
          </a>{" "}
          or chat with us, or the community on
          <a href="https://discord.gg" className=" pl-1 text-customGreen underline">
            Discord
          </a>
          .
        </p>
      </section>

      {/* Getting Started Guide */}
      <section className="text-center py-12">
        <h2 className="text-3xl text-customGreen font-semibold mb-6">
          Common Questions
        </h2>
        <Accordion
          title="Where I can get Technical Support?"
          content="The best way to get support is through our discord channel."
        />
         <Accordion
          title="Is AI arena free?"
          content="Yes, but you can get additional perks by donating. Donations directly contributes to creating a better experience for all participants."
        />
      </section>

      {/* Support Us via Patreon */}
      <section className="text-center py-12 ">
      <h2 className="text-4xl font-bold text-customGreen text-center mb-8">
        Support Us on Patreon
      </h2>
      <p className="mb-4 text-lg max-w-2xl mx-auto">
          AI arena is a nonprofit organization, any donations will
          be used to increase the quality and amount of streams, server
          throughput, and website functionality. Our expenses and incomes are publicly available at <a href="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903" className="text-customGreen underline">
              Project Finance
            </a>.
        </p>
    
        <SubscriptionList/>
        <MainButton text="Donate" key={"patronbutton"} href={footerLinks.socialLinks[1].href}/>
      </section>


      {/* Troubleshooting & Contributions */}
      <section className="text-center py-12">
        <h2 className="text-3xl text-customGreen font-semibold mb-6">
          Technical Support & Questions
        </h2>
        <p className="text-lg  max-w-lg mx-auto">
          For troubleshooting, visit our  
          <a href="https://discord.gg" className="pl-1 text-customGreen underline">
            Discord
          </a>{" "}
          or check out our
          <a href="/wiki" className="pl-1 text-customGreen underline">
            wiki
          </a>{" "}
          for contributing information.
        </p>
      </section>
    </ArticleWrapper>
  );
};

export default AboutUs;
