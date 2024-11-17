import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Supporters } from "@/_data/footerLinks";
import WrappedTitle from "@/_components/_display/WrappedTitle";

interface SupportersComponentProps {
  supporters: Supporters[];
}

const SupportersComponent: React.FC<SupportersComponentProps> = ({
  supporters,
}) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
     <WrappedTitle title="Funded by You"/>
      <p className="text-lg mb-6">{supporters[0].name}</p>
      <p className="text-lg mb-6">
        Thank you for your support! Your contributions help us keep going.
      </p>
      <div className="flex justify-center">
        <Link href="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903">
          <div className="flex items-center">
            <Image
              alt="Excel-Icon"
              src={`${process.env.PUBLIC_PREFIX}/icons/excel-icon.svg`}
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
