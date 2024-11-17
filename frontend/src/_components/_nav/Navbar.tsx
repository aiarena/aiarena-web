"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import NavItem from "./_nav_parts/NavItem";
import MobileNavitem from "./_nav_parts/MobileNavItem";
import MobileNavItem from "./_nav_parts/MobileNavItem";
import AuthNavBar from "./_nav_parts/AuthNavbar";


const navLinks = [
  {
    title: "Home",
    path: "/",
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
    path: "/competitions",
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "About us",
    path: "/about",
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "Profile",
    path: "/profile",
    showLoggedIn: true,
    showLoggedOut: false,
  },
  {
    title: "Examples",
    path: "/examples",
    showLoggedIn: true,
    showLoggedOut: true,
  },
  {
    title: "ToDo",
    path: "/todo",
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
      <nav className="w-full bg-neutral-900 px-2 text-white dark:bg-gray-900 font-sans">
        <div className="flex justify-between md:p-3 md:flex ">
          
            <Link href="/" className="flex justify-between items-center">

            <Image className="pr-2 invert" src={`${process.env.PUBLIC_PREFIX}/assets_logo/ai-arena-logo.svg`} alt="AI-arena-logo" width={50} height={50}></Image>
              <h2 className="text-2xl font-bold md:5pl:5 py-4 md:py-0">
                {navbarTitle.title}
              </h2>
           
            </Link>
       

          {/* Phone */}
          <div className="md:hidden py-4">
            <button className="py-3 rounded-md" onClick={() => handleMenu()}>
              {navbar ? (
                <div>
                  <Image
                    src={`${process.env.PUBLIC_PREFIX}/cross.svg`}
                    width={25}
                    height={25}

                    alt="close"
                    className="invert"
                  />
                </div>
              ) : (
                <Image
                  src={`${process.env.PUBLIC_PREFIX}/menu.svg`}
                  width={25}
                  height={25}
                  alt="menu"
                  className="invert"
                />
              )}
            </button>
          </div>

          {/* pc nav */}
          <div className="hidden md:block">
            <ul className="flex">
              {navLinks.map((link, index) => (
                <div key={index}>
                  { 
                    <NavItem
                      key={index}
                      href={link.path}
                      onClick={handleWindowResize}
                    >
                      {link.title}
                    </NavItem>
                  }
                </div>
              ))}
              <li>
                <AuthNavBar />
                
              </li>
            </ul>
          </div>
        </div>
        {navbar === true ? (
          <div className={` md block ${navbar ? "block" : "hidden"}`}>
            <ul className="md:h-auto md:flex mt-8 h-screen">
              {navLinks.map((link, index) => (
                <div key={index}>
                  {
                    <MobileNavItem
                      key={index}
                      href={link.path}
                      onClick={handleWindowResize}
                    >
                      {link.title}
                    </MobileNavItem>
                  }
                </div>
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
