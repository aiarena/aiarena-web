import Link from "next/link";
import React from "react";

interface FooterNavItemProps {
  href: string;
  name: string;
}

const FooterNavItem: React.FC<FooterNavItemProps> = ({ href, name }) => {
  return (
    <li>
      <Link href={href} className="hover:underline">
        {name}
      </Link>
    </li>
  );
};

export default FooterNavItem;
