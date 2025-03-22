import Image from "next/image";
import Link from "next/link";
import React from "react";

interface FooterNavItemProps {
  icon: string;
  invertIcon: boolean;
  href: string;
  name: string;
}

const FooterNavItem: React.FC<FooterNavItemProps> = ({
  icon,
  href,
  name,
  invertIcon,
}) => {
  return (
    <li>
      <div className="flex ">
        <Link href={href} className="hover:underline">
          <div className="flex ">
            <Image
              src={icon}
              alt={name + "-Icon"}
              width={24}
              height={24}
              className={`mr-2 w-6 h-6 ${invertIcon ? "invert" : ""}`}
            />
            {name}
          </div>
        </Link>
      </div>
    </li>
  );
};

export default FooterNavItem;
