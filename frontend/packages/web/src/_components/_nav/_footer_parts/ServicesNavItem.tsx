import React from "react";
import FooterNavItem from "./FooterNavItem";
import { FooterLink } from "@/_data/footerLinks";
import Link from "next/link";

import WrappedTitle from "@/_components/_display/WrappedTitle";

interface ServicesComponentProps {
  services: FooterLink[];
}

const ServicesComponent: React.FC<ServicesComponentProps> = ({ services }) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 w-full">
      <WrappedTitle title="Our Services"/>
      <ul className="space-y-2">
        <p>Im not really sure what to put here...</p>
        <p> Maybe list games?</p>
        <li>
          <Link href={"Apokerpage"}> Starcraft 2 </Link>
        </li>
        <li>
          <Link href={"Apokerpage"}>Poker</Link>
        </li>
      </ul>
    </div>
  );
};

export default ServicesComponent;
