import { Link } from "react-router";
import React from "react";
import clsx from "clsx";

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
      <div className="flex">
        <Link to={href} className="hover:underline">
          <div className="flex">
            <img
              src={icon}
              alt={name + "-Icon"}
              width={24}
              height={24}
              className={clsx("mr-2", "w-6", "h-6", invertIcon && "invert")}
            />
            {name}
          </div>
        </Link>
      </div>
    </li>
  );
};

export default FooterNavItem;
