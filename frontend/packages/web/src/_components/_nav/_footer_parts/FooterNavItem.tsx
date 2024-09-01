import Image from "next/image";
import Link from "next/link";
import React from "react";

interface FooterNavItemProps {
  icon:string;
  invertIcon: boolean;
  href: string;
  name: string;
}

const FooterNavItem: React.FC<FooterNavItemProps> = ({ icon, href, name,invertIcon }) => {
  return (
    <li>
      <div className="flex ">
      <Link href={href} className="hover:underline">
      <div className="flex ">
       <Image src={icon} alt={name + "-Icon"} width={25} height={20} className={`mr-2 ${invertIcon ? "invert" : ""}`}/>
        {name}
        </div>
      </Link>
      </div>
    </li>
  );
};

export default FooterNavItem;
