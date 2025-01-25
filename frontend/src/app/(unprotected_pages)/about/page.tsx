"use client";

import TitleWrapper from "@/_components/_display/TitleWrapper";
import Accordion from "@/_components/_examples/Accordion";
import Button from "@/_components/_props/Button";
import MainButton from "@/_components/_props/MainButton";
import Image from "next/image";
import React from "react";
import { FooterLink, footerLinks } from "@/_data/footerLinks";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import SubscriptionList from "@/_components/_display/SubscriptionList";
import SectionDivider from "@/_components/_display/SectionDivider";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";

const AboutUs = () => {
  return (
    <>
    <ArticleWrapper className="bg-customBackgroundColor2 text-white">
      {/* AI Arena Overview */}
      <section className="py-12 bg-customBackgroundColor2D1 ">
        <h1 className="text-4xl text-customGreen font-bold text-center mb-8">
          What is <span className="font-gugi">AI Arena</span>?
        </h1>
        <p className="text-lg max-w-2xl mx-auto text-center leading-relaxed">
          AI Arena is a nonprofit platform dedicated to advancing artificial
          intelligence through competitive StarCraft II matches. Designed for
          AI researchers, enthusiasts, and developers, our platform features
          ranked ladders, real-time game streams, and performance analytics.
          Join us on{" "}
          <a href="https://twitch.tv" className="pl-1 text-customGreen underline">
            Twitch
          </a>{" "}
          to watch live matches, or connect with our community on{" "}
          <a href="https://discord.gg" className="pl-1 text-customGreen underline">
            Discord
          </a>
          .
        </p>
      </section>

      <SectionDivider darken={1} />

      {/* Getting Started Guide */}
      <section className="py-12 bg-customBackgroundColor3">
   
        <div className="max-w-2xl mx-auto">
          <Accordion
            title="How can I get started with AI Arena?"
            content="To get started, register on our platform, read our Getting Started guide, and upload your AI bot for competition. Detailed instructions are available on our Wiki page."
          />
          <Accordion
            title="Where can I get technical support?"
            content="For assistance, join our Discord community or check the troubleshooting section on our Wiki page."
          />
          <Accordion
            title="Is AI Arena free?"
            content="Yes, AI Arena is free to use, but you can support us through donations to unlock additional perks and enhance the platform."
          />
        </div>
      </section>

      <SectionDivider darken={1} />

      {/* Support Us via Patreon */}
      <section className="py-12 bg-customBackgroundColor2D1">
        <h2 className="text-4xl font-bold text-customGreen text-center mb-8">
          Why Support AI Arena?
        </h2>
        <p className="mb-4 text-lg max-w-2xl mx-auto text-center leading-relaxed">
          By supporting AI Arena, you help us maintain and expand our platform.
          Donations fund server costs, streaming improvements, and new features
          to enhance the competitive AI experience. Our financial details are
          publicly accessible for transparency. Learn more in our{" "}
          <a
            href="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903"
            className="text-customGreen underline"
          >
            Project Finance
          </a>{" "}
          document.
        </p>
        <SubscriptionList />
        <div className="mt-6">
          <MainButton
            text="Donate Now"
            key={"patronbutton"}
            href={footerLinks.socialLinks[1].href}
          />
        </div>
      </section>

      <SectionDivider darken={1} />

      {/* Troubleshooting & Contributions */}
      <section className="py-12 bg-customBackgroundColor3">
        <h2 className="text-3xl text-customGreen font-semibold text-center mb-6">
          Troubleshooting and Contributions
        </h2>
        <p className="text-lg max-w-lg mx-auto text-center leading-relaxed">
          Facing issues? Visit our{" "}
          <a
            href="https://discord.gg"
            className="pl-1 text-customGreen underline"
          >
            Discord
          </a>{" "}
          for help from our active community or refer to our{" "}
          <a href="/wiki" className="pl-1 text-customGreen underline">
            Wiki
          </a>
          . Interested in contributing? Share your ideas or collaborate on
          improving AI Arena with us.
        </p>
      </section>
    </ArticleWrapper>
    <PreFooterSpacer/>
    </>
  );
};

export default AboutUs;
