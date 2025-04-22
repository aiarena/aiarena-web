import React from "react";
// import Link from "next/link";
// import Image from "next/image";
import { Supporters } from "@/_data/footerLinks";
// import WrappedTitle from "@/_components/_display/WrappedTitle";
// import { getPublicPrefix } from "@/_lib/getPublicPrefix";

// import { getFeatureFlags } from "@/_data/featureFlags";
import { Link } from "react-router";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import WrappedTitle from "@/_components/_display/WrappedTitle";

interface SupportersComponentProps {
  supporterData: Supporters[];
}

const SupportersComponent: React.FC<SupportersComponentProps> = ({
  supporterData,
}) => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
      <WrappedTitle title="Funded by You" />
      <p className="text-lg mb-6">{supporterData[0].name}</p>
      <p className="text-lg mb-6">
        Thank you for your support! <br /> Your contributions help us keep
        going.
      </p>
      <div className="flex justify-center">
        <Link to="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903">
          <div className="flex items-center">
            <img
              alt="Excel-Icon"
              src={`${getPublicPrefix()}/icons/excel-icon.svg`}
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
