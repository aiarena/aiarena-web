import { useState, useEffect } from "react";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { NavLink } from "react-router";
import { navbarTitle, navLinks } from "@/_data/navbarLinks";
import clsx from "clsx";
import BackgroundTexture from "../_display/BackgroundTexture";
import AuthNavbar from "./AuthNavbar";

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
    if (window.innerWidth >= 760) {
      setNavbar(false);
      document.body.style.overflow = "unset";
    }
  };

  const handleMobileNavItemClick = () => {
    setNavbar(false);
    document.body.style.overflow = "unset";
  };

  useEffect(() => {
    window.addEventListener("resize", handleWindowResize);
    return () => {
      window.removeEventListener("resize", handleWindowResize);
    };
  }, []);

  return (
    <>
      <nav className="w-full  text-white sticky top-0 z-50  bg-neutral-700 ">
        <BackgroundTexture>
          <div className="flex px-2 justify-between md:p-3 md:flex bg-darken-3 md:shadow-sm shadow-black border-neutral-700 border-b">
            <a
              href={navLinks[0].path}
              className="flex justify-between items-center"
            >
              <img
                className="pr-2 invert"
                src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
                alt="AI-arena-logo"
                width={48}
                height={48}
              />
              <h2 className="text-2xl md:pl-5 py-4 md:py-0 pb-5 font-gugi font-light text-customGreen hover:text-white text-center">
                {navbarTitle.title}
              </h2>
            </a>

            {/* Phone */}
            <div className="md:hidden py-4">
              <button
                className="py-3 rounded-md px-3 cursor-pointer"
                onClick={handleMenu}
              >
                {navbar ? (
                  <div>
                    <img
                      src={`${getPublicPrefix()}/icons/cross.svg`}
                      width={24}
                      height={24}
                      alt="Close menu"
                      className="invert w-6 h-6"
                    />
                  </div>
                ) : (
                  <img
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
              <div className="flex flex-col">
                <ul className="flex flex-wrap">
                  {navLinks
                    .filter((it) => it.featureFlag !== false)
                    .map((link, index) => (
                      <li key={index} className="pb-2 text-l p-2 text-center">
                        {link.react === true ? (
                          <NavLink
                            key={index}
                            to={link.path}
                            className={({ isActive }) =>
                              clsx(
                                "py-2 text-white border-b-2",
                                isActive
                                  ? "border-customGreen"
                                  : "border-transparent hover:border-customGreen"
                              )
                            }
                          >
                            {link.title}
                          </NavLink>
                        ) : (
                          <a
                            key={index}
                            href={link.path}
                            className={clsx(
                              "py-2 text-white border-b-2",
                              window.location.pathname === link.path
                                ? "border-customGreen"
                                : "border-transparent hover:border-customGreen"
                            )}
                          >
                            {link.title}
                          </a>
                        )}
                      </li>
                    ))}
                  <AuthNavbar />
                </ul>
              </div>
            </div>
          </div>
          {navbar === true ? (
            <div className={clsx("md:block", navbar ? "block" : "hidden")}>
              <ul className="md:h-auto md:flex bg-darken-3 pt-8 h-screen max-h-[calc(100vh-3rem)] overflow-y-auto">
                {navLinks
                  .filter((it) => it.featureFlag !== false)
                  .map((link, index) => (
                    <li key={index} className="text-l p-2 text-center w-full">
                      <a
                        key={index}
                        href={link.path}
                        onClick={handleMobileNavItemClick}
                        className={clsx(
                          "block w-full bg-darken-3 hover:darken-4 py-2 text-white hover:text-slate-300 border-b-2",
                          window.location.pathname === link.path
                            ? "border-customGreen"
                            : "border-transparent"
                        )}
                      >
                        {link.title}
                      </a>

                      {/* Alternative NavLink block kept as-is (commented) */}
                      {/* 
                  <NavLink
                    key={index}
                    to={link.path}
                    onClick={handleMobileNavItemClick}
                    className={({ isActive }) =>
                      clsx(
                        "block w-full bg-slate-800 hover:bg-slate-700 py-2 text-white hover:text-slate-300 border-b-2",
                        isActive
                          ? "border-customGreen"
                          : "border-transparent"
                      )
                    }
                  >
                    {link.title}
                  </NavLink>
                  */}
                    </li>
                  ))}
              </ul>
            </div>
          ) : null}
        </BackgroundTexture>
      </nav>
    </>
  );
}

export default Navbar;
