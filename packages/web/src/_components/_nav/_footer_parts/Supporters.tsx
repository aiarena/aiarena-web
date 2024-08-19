import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Supporters } from "@/_data/footerLinks";

interface SupportersComponentProps {
  supporters: Supporters[];
}

const SupportersComponent: React.FC<SupportersComponentProps> = ({
  supporters,
}) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
  <div className="flex items-center mb-4 justify-center relative">
          <div className="flex-1 h-[2px] bg-gradient-to-l from-customGreen to-transparent"></div>
      <h2 className="text-2xl font-bold p-2">Funded by you</h2>
      <div className="flex-1 h-[2px] bg-gradient-to-r from-customGreen to-transparent"></div>
      </div>
      <p className="text-lg mb-6">{supporters[0].name}</p>
      <p className="text-lg mb-6">
        Thank you for your support! Your contributions help us keep going.
      </p>
      <div className="flex justify-center">
        <Link href="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903">
          <div className="flex items-center">
            <Image
              alt="Excel-Icon"
              src={"/icons/excel-icon.svg"}
              height={35}
              width={35}
              className="pr-2"
            />
            <p className="text-customGreen text-lg hover:text-white transition">
              Project Finance
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default SupportersComponent;
