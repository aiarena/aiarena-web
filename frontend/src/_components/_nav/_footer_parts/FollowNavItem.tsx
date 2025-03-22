import Link from "next/link";
import React from "react";
import { FollowIcon } from "@/_data/footerLinks";

interface FollowComponentProps {
  icons: FollowIcon[];
}

const FollowComponent: React.FC<FollowComponentProps> = ({ icons }) => {
  return (
    <div className="mb-4 md:mb-0">
      <h4 className="text-lg font-semibold mb-2">Follow Us</h4>
      <div className="flex space-x-4">
        {icons.map((icon, index) => (
          <Link
            href={icon.href}
            key={index}
            className="hover:text-gray-400 cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={icon.icon}
              />
            </svg>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default FollowComponent;
