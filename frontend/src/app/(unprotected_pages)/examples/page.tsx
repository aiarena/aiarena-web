"use client";
import CompetitionData from "@/_components/_display/CompetitionData";
import Accordion from "@/_components/_examples/Accordion";
import Card from "@/_components/_examples/Card";
import HoverCard from "@/_components/_examples/Card";
import FeatureCard from "@/_components/_examples/FeatureCard";
import GradientButton from "@/_components/_examples/GradientButton";
import NotificationBanner from "@/_components/_examples/NotificationBanner";
import PricingCard from "@/_components/_examples/PricingCard";
import ProfileCard from "@/_components/_examples/ProfileCard";
import ProgressBar from "@/_components/_examples/ProgressBar";
import StatCard from "@/_components/_examples/StatCard";
import StatsOverview from "@/_components/_examples/StatsOverview";
import TestimonialsCarousel from "@/_components/_examples/TestimonalsCarousel";
import TitleBanner from "@/_components/_examples/TitleBanner";
import React from "react";

const ExamplePage: React.FC = () => {
  return (
    <>
      <div className="container mx-auto py-8">
        <CompetitionData />

        <Accordion
          title="What is AI Arena?"
          content="AI Arena is a platform where you can compete with AI models."
        />
        <Accordion
          title="How can i get started?"
          content="AI Arena is a platform where you can compete with AI models."
        />

        <ProgressBar percentage={75} />
        <div className="circular-gradient-shadow"></div>
        <div className="p-6 md:p-10 rounded-xl shadow-2xl mb-12 border-4 border-gray-300 animate-sine-wave bg-gradient-to-br from-black via-[rgba(0,194,50,0.5)] via-70% to-[rgba(0,0,0,1)] overflow-hidden">
          <h1 className="flex flex-wrap">
            An example of&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
            text.
          </h1>
          <p className="flex flex-wrap">
            With a&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
            Box.
          </p>
        </div>
        <div className="p-6 md:p-10 rounded-xl shadow-2xl mb-12 border-4 border-gray-300 animate-sine-wave bg-gradient-to-br from-black to-[rgba(134,194,50,1)] overflow-hidden">
          <h1 className="flex flex-wrap">
          An example of&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
          text.
          </h1>
          <p className="flex flex-wrap">
          With a&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
            Box.
          </p>
        </div>

        <div className="p-6 md:p-10 rounded-xl shadow-2xl mb-12 border-4 border-gray-300 animate-sine-wave bg-gradient-to-br from-black to-transparent overflow-hidden">
          <h1 className="flex flex-wrap">
          An example of&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
          text.
          </h1>
          <p className="flex flex-wrap">
          With a&nbsp;<b className="animate-sine-wave-text">SHINY&nbsp;</b>
            Box.
          </p>
        </div>
        <div className="dividing-line1"></div>
        <br />
        <br />
        <div className="dividing-line2"></div>
        <br />
        <br />
        <div className="dividing-line3"></div>
        <br />
        <br />
        <div className="dividing-line4"></div>
        <br />
        <br />
        <div className="dividing-line5"></div>
        <br />
        <br />
        <div className="dividing-line6"></div>
        <br />
        <br />
        <div className="dividing-line7"></div>
        <br />
        <br />
        <div className="dividing-line8"></div>
        <br />
        <br />
        <div className="dividing-line9"></div>
        <br />
        <br />
        <div className="dividing-line10"></div>
        <br />
        <br />
      </div>
      <div className="container mx-auto py-8 space-y-8">
        <TitleBanner
          title="Welcome to Our Platform"
          subtitle="Explore the amazing features we offer"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card
            title="Amazing Feature"
            description="Discover how this feature can enhance your experience."
            imageUrl={`${process.env.PUBLIC_PREFIX}/competitions/sc2_1.webp`}
          />
          {/* <Card
           title="Another Great Feature"
           description="Learn more about the benefits of using this feature."
           imageUrl="https://source.unsplash.com/random"
         />
         <Card
           title="Our Mission"
           description="Understand our mission and vision for the future."
           imageUrl="https://source.unsplash.com/random"
         /> */}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            title="Rocket Speed"
            description="Experience unmatched speed and performance."
            icon={`${process.env.PUBLIC_PREFIX}/icons/excel-icon.svg`}
          />
          <FeatureCard
            title="Community Support"
            description="Join a community of like-minded individuals."
            icon={`${process.env.PUBLIC_PREFIX}/icons/excel-icon.svg`}
          />
          <StatCard stat="99.9%" description="Uptime Guarantee" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <ProfileCard
            name="Jane Doe"
            role="Lead Developer"
            imageUrl={`${process.env.PUBLIC_PREFIX}/competitions/sc2_1.webp`}
            bio="Jane has over 10 years of experience in full-stack development and is passionate about building scalable web applications."
          />
          <ProfileCard
            name="John Smith"
            role="Product Manager"
            imageUrl={`${process.env.PUBLIC_PREFIX}/competitions/sc2_1.webp`}
            bio="John is dedicated to ensuring our products meet the needs of our users and consistently exceed expectations."
          />
        </div>
        <div className="container mx-auto py-8 space-y-8">
          <TitleBanner title="What Our Users Say" />
          <TitleBanner title="Our Pricing Plans" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <PricingCard
              plan="Basic"
              price="$19/mo"
              features={["Feature 1", "Feature 2", "Feature 3"]}
            />
            <PricingCard
              plan="Pro"
              price="$49/mo"
              features={["Feature 1", "Feature 2", "Feature 3", "Feature 4"]}
              isPopular
            />
            <PricingCard
              plan="Enterprise"
              price="Contact Us"
              features={[
                "Feature 1",
                "Feature 2",
                "Feature 3",
                "Feature 4",
                "Feature 5",
              ]}
            />
          </div>
          <div className="text-center">
            <GradientButton
              text="Get Started"
              onClick={() => alert("Button clicked!")}
            />
          </div>
          <TitleBanner title="Key Metrics" />
          <StatsOverview
            stats={[
              { label: "Users", value: "1,200+" },
              { label: "Projects", value: "340" },
              { label: "Support Tickets", value: "23" },
              { label: "Partners", value: "50+" },
            ]}
          />
          <TitleBanner title="Some buttons" />
          <button className="bg-gradient-green-lime text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-green-olive text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-green-yellow text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-1 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-2 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-3 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-green-teal-gradient text-white font-bold py-2 px-4 rounded-lg border-2 border-softTeal hover:bg-softTeal">
            Green to Teal
          </button>
          <button className="bg-green-yellow-gradient text-white font-bold py-2 px-4 rounded-xl border-2 border-mellowYellow hover:bg-mellowYellow">
            Green to Yellow
          </button>
          <button className="bg-teal-yellow-gradient text-white font-bold py-2 px-4 rounded-lg border-2 border-customGreen hover:bg-customGreen">
            Teal to Yellow
          </button>
          <div className="text-center">
            <TitleBanner title="Competitons" />
            <h1 className="text-4xl font-bold">Competition</h1>
            <p>
              <b>Filter for game click/dropdown</b>
            </p>
            <p>Active competitions</p>
            <p>- some more stats here, top 3 bots, etc</p>
            should take 60% of page
            <p> A progress bar for duration would be cool</p>
            <br />
            <br />
            <p>Past competitions</p>
            <p> Keep a list style but adding search/etc</p>
            <p className="text-lg mt-4">------------------</p>
          </div>
          <div>
            <p> inside an active competiton.</p>
            <p>
              {" "}
              It seems reasonable to seperate match history / match queue by
              competition
            </p>
            <p>
              {" "}
              it seems also reasonable to add link to twitch stream inside the
              competition - if twitch is playing current competition
            </p>
          </div>
          ------------------
          <div>
            <p>
              {" "}
              Public bots are pretty interesting though. - they should
              definitely have a -highest elo- or similar for sort.
            </p>
            <p>
              {" "}
              the statistics for bots/authors are amazing. - But there needs to
              be some form of sort
            </p>

            <p>
              {" "}
              I think initially hide authors. Sort bots for total elo, or
              competition placings etc.{" "}
            </p>
            <p>
              would be nice with some form of accumulative points for winning a
              competition
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default ExamplePage;
