import { useState, useEffect } from "react";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { Link, NavLink } from "react-router";
import { navbarTitle, navLinks } from "@/_data/navbarLinks";

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
      <nav className="w-full bg-neutral-900 px-2 text-white sticky top-0 z-50">
        <div className="flex justify-between md:p-3 md:flex ">
          <Link
            to={navLinks[0].path}
            className="flex justify-between items-center"
          >
            <img
              className="pr-2 invert"
              src={`${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`}
              alt="AI-arena-logo"
              width={48}
              height={48}
            />
            <h2 className="text-2xl font-bold md:5pl:5 py-4 md:py-0 pb-5 font-gugi">
              {navbarTitle.title}
            </h2>
          </Link>

          {/* Phone */}
          <div className="md:hidden py-4">
            <button
              className="py-3 rounded-md px-3 cursor-pointer"
              onClick={() => handleMenu()}
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
            {/* Container for Nav Items */}
            <div className="flex flex-col">
              <ul className="flex flex-wrap">
                {navLinks.map((link, index) => (
                  <li key={index} className={`pb-2 text-l p-2  text-center`}>
                    <NavLink
                      to={link.path}
                      onClick={handleWindowResize}
                      className={({ isActive }) =>
                        `py-2 hover:text-slate-300 text-white ${isActive ? "border-b-2 border-customGreen" : "border-b-2 border-transparent"}`
                      }
                    >
                      {link.title}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>

            {/* Auth NavBar stays top-right */}
            {/* <div className="ml-auto">
              <AuthNavBar />
            </div> */}
          </div>
        </div>
        {navbar === true ? (
          <div className={`md:block ${navbar ? "block" : "hidden"}`}>
            <ul className="md:h-auto md:flex mt-8 h-screen max-h-[calc(100vh-7rem)] overflow-y-auto">
              {navLinks.map((link, index) => (
                <li key={index} className="text-l p-2 text-center w-full">
                  <NavLink
                    key={index}
                    to={link.path}
                    onClick={handleMobileNavItemClick}
                    className={({ isActive }) =>
                      `block w-full bg-slate-800 hover:bg-slate-700 py-2 text-white hover:text-slate-300 ${
                        isActive
                          ? "border-b-2 border-customGreen"
                          : "border-b-2 border-transparent"
                      }`
                    }
                  >
                    {link.title}
                  </NavLink>
                </li>
              ))}

              <li className="flex justify-center pb-10">
                {/* <AuthNavBar /> */}
              </li>
            </ul>
          </div>
        ) : null}
      </nav>
    </>
  );
}

export default Navbar;
