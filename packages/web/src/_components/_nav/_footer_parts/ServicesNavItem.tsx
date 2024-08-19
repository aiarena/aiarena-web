import React from "react";
import FooterNavItem from "./FooterNavItem";
import { FooterLink } from "@/_data/footerLinks";
import Link from "next/link";

interface ServicesComponentProps {
  services: FooterLink[];
}

const ServicesComponent: React.FC<ServicesComponentProps> = ({ services }) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
       <div className="flex items-center mb-4 justify-center relative">
          <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
      <h2 className="text-2xl font-bold p-2">Our Services</h2>
      <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
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
