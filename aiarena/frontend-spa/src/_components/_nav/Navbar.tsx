import { useState, useEffect, Suspense } from "react";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { Link, NavLink } from "react-router";
import { navbarTitle, navLinks } from "@/_data/navbarLinks";
import clsx from "clsx";
import BackgroundTexture from "../_display/BackgroundTexture";
import AuthNavbar from "./AuthNavbar";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

function Navbar() {
  const [navbar, setNavbar] = useState(false);

  const handleMenu = () => {
    if (navbar) {
      setNavbar(false);
      document.body.style.overflow = "unset";
    } else {
      setNavbar(true);
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
    <nav className="w-full text-white sticky top-0 z-50 bg-neutral-700">
      <BackgroundTexture>
        <div className="flex px-2 justify-between md:px-3 md:py-1 md:flex bg-darken-3 md:shadow-sm shadow-black border-neutral-700 border-b">
          <Link
            to={navLinks[0].path}
            className="animate-press flex justify-between items-center"
          >
            <img
              className="pr-2 invert"
              src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
              alt="AI-arena-logo"
              width={48}
              height={48}
            />

            <h2 className="text-2xl md:pl-5 py-0 md:py-0 font-gugi font-light text-customGreen hover:text-white text-center">
              {navbarTitle.title}
            </h2>
          </Link>

          {/* Phone */}
          <div className="md:hidden py-1">
            <button
              className="py-3 rounded-md px-3 cursor-pointer"
              onClick={handleMenu}
            >
              {navbar ? (
                <img
                  src={`${getPublicPrefix()}/icons/cross.svg`}
                  width={24}
                  height={24}
                  alt="Close menu"
                  className="invert w-6 h-6"
                />
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

          {/* Desktop nav */}
          <div className="ml-40 hidden md:flex justify-between">
            <div className="flex flex-col">
              <ul className="flex flex-wrap">
                {navLinks
                  .filter((it) => it.featureFlag !== false)
                  .map((link, index) => (
                    <li key={index} className="text-l py-2 px-2 text-center">
                      {link.react === true ? (
                        <NavLink
                          to={link.path}
                          className={({ isActive }) =>
                            clsx(
                              "animate-press inline-block py-[0.3em] text-white border-b-2",
                              isActive
                                ? "border-customGreen"
                                : "border-transparent hover:border-customGreen",
                            )
                          }
                        >
                          {link.title}
                        </NavLink>
                      ) : (
                        <a
                          href={link.path}
                          target="_blank"
                          className={clsx(
                            "animate-press inline-block py-[0.3em] text-white border-b-2",
                            window.location.pathname === link.path
                              ? "border-customGreen"
                              : "border-transparent hover:border-customGreen",
                          )}
                        >
                          <span className="flex items-center justify-center gap-1">
                            {link.title}
                            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                          </span>
                        </a>
                      )}
                    </li>
                  ))}

                <Suspense
                  fallback={
                    <li className="text-l py-2 px-1 text-center w-26">
                      <span className="h-[30px] flex items-center justify-center">
                        <LoadingSpinner />
                      </span>
                    </li>
                  }
                >
                  <li className="text-l py-2 px-1 text-center w-26">
                    <ErrorBoundaryWrapper override="Error">
                      <AuthNavbar />
                    </ErrorBoundaryWrapper>
                  </li>
                </Suspense>
              </ul>
            </div>
          </div>
        </div>

        {/* Mobile nav */}
        {navbar ? (
          <div className="block md:block">
            <ul className="md:h-auto md:flex bg-darken-3 pt-8 h-screen max-h-[calc(100vh-3rem)] overflow-y-auto pb-32">
              {navLinks
                .filter((it) => it.featureFlag !== false)
                .map((link, index) => (
                  <li key={index} className="text-l p-2 text-center w-full">
                    {link.react === true ? (
                      <NavLink
                        to={link.path}
                        onClick={handleMobileNavItemClick}
                        className={({ isActive }) =>
                          clsx(
                            "animate-press block w-full bg-darken-3 hover:bg-darken-4 py-2 text-white hover:text-slate-300 border-b-2",
                            isActive
                              ? "border-customGreen"
                              : "border-transparent",
                          )
                        }
                      >
                        {link.title}
                      </NavLink>
                    ) : (
                      <a
                        href={link.path}
                        onClick={handleMobileNavItemClick}
                        className={clsx(
                          "animate-press block w-full bg-darken-3 hover:bg-darken-4 py-2 text-white hover:text-slate-300 border-b-2",
                          window.location.pathname === link.path
                            ? "border-customGreen"
                            : "border-transparent",
                        )}
                      >
                        <span className="flex items-center justify-center gap-1">
                          {link.title}
                          <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                        </span>
                      </a>
                    )}
                  </li>
                ))}

              <Suspense
                fallback={
                  <li className="text-l p-2 text-center w-full">
                    <span className="h-[42px] flex items-center justify-center">
                      <LoadingSpinner />
                    </span>
                  </li>
                }
              >
                <li className="text-l p-2 text-center w-full">
                  <ErrorBoundaryWrapper>
                    <AuthNavbar mobile />
                  </ErrorBoundaryWrapper>
                </li>
              </Suspense>
            </ul>
          </div>
        ) : null}
      </BackgroundTexture>
    </nav>
  );
}

export default Navbar;
