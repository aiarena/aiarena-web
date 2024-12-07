"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import NavItem from "./_nav_parts/NavItem";
import MobileNavitem from "./_nav_parts/MobileNavItem";
import MobileNavItem from "./_nav_parts/MobileNavItem";
import AuthNavBar from "./_nav_parts/AuthNavbar";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";


const navLinks = [
  {
    title: "Home",
    path: `${getPublicPrefix()}/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Wiki",
    path: "https://aiarena.net/wiki/",
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Competitions",
    path: `${getPublicPrefix()}/competitions/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "About us",
    path: `${getPublicPrefix()}/about/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Status",
    path: `${getPublicPrefix()}/status/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Bots",
    path: `${getPublicPrefix()}/bots/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Profile",
    path: `${getPublicPrefix()}/profile/`,
    showLoggedIn: true,
    showLoggedOut: false,
  },
  {
    title: "Examples",
    path: `${getPublicPrefix()}/examples/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "ToDo",
    path: `${getPublicPrefix()}/todo/`,
    showLoggedIn: true,
    showLoggedOut: true,
  },
];

const navbarTitle = {
  title: "AI Arena",
};

function Navbar() {
  const [navbar, setNavbar] = useState(false);


  const handleMenu = () => {
    if (navbar === true) {
      setNavbar(!navbar);
      document.body.style.overflow = "unset";
    } else {
      setNavbar(!navbar);
      document.body.style.overflow = "hidden";
    }
  };

  const handleWindowResize = () => {
    console.log("resized screen");
    if (window.innerWidth >= 760) {
      // Only close the navbar on larger screens
      setNavbar(false);
      document.body.style.overflow = "unset";
    }
  };

  const handleMobileNavItemClick = () => {
    setNavbar(false);
    document.body.style.overflow = "unset";
  };

  useEffect(() => {
    // Add event listener when the component mounts
    window.addEventListener("resize", handleWindowResize);

    // Clean up the event listener when the component unmounts
    return () => {
      window.removeEventListener("resize", handleWindowResize);
    };
  }, []);

  return (
    <>
      <nav className="w-full bg-neutral-900 px-2 text-white dark:bg-gray-900 font-sans sticky top-0 z-50">
        <div className="flex justify-between md:p-3 md:flex ">
          <Link href={`${getPublicPrefix()}`} className="flex justify-between items-center">
            <Image
              className="pr-2 invert h-[auto] w-12"
              src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
              alt="AI-arena-logo"
              width={48}
              height={48}
            ></Image>
            <h2 className="text-2xl font-bold md:5pl:5 py-4 md:py-0 pb-5">
              {navbarTitle.title}
            </h2>
          </Link>

          {/* Phone */}
          <div className="md:hidden py-4">
            <button className="py-3 rounded-md pr-4" onClick={() => handleMenu()}>
              {navbar ? (
                <div>
                  <Image
                    src={`${getPublicPrefix()}/icons/cross.svg`}
                    width={24}
                    height={24}
                    alt="Close menu"
                    className="invert w-6 h-6"
                  />
                </div>
              ) : (
                <Image
                  src={`${getPublicPrefix()}/icons/menu.svg`}
                  width={24}
                  height={24}
                  alt="menu"
                  className="invert w-6 h-6"
                />
              )}
            </button>
          </div>
          {/* pc nav */}
          <div className="ml-40 hidden md:flex justify-between">
            {/* Container for Nav Items */}
            <div className="flex flex-col">
              <ul className="flex flex-wrap">
                {navLinks.map((link, index) => (
              <li
              key={index}
           
            >
                    <NavItem href={link.path} onClick={handleWindowResize}>
                      {link.title}
                    </NavItem>
                  </li>
                ))}
              </ul>
            </div>

            {/* Auth NavBar stays top-right */}
            <div className="ml-auto">
              <AuthNavBar />
            </div>
          </div>
        </div>
        {navbar === true ? (
          <div className={` md block ${navbar ? "block" : "hidden"}`}>
            <ul className="md:h-auto md:flex mt-8 h-screen">
              {navLinks.map((link, index) => (
                     <li
                     key={index}
                    
                   >
                  {
                    <MobileNavItem
                      key={index}
                      href={link.path}
                      onClick={handleMobileNavItemClick}
                    >
                      {link.title}
                    </MobileNavItem>
                  }
                </li>
              ))}

              <li>
                <AuthNavBar />
              </li>
            </ul>
          </div>
        ) : null}
      </nav>
    </>
  );
}

export default Navbar;
