import React from "react";
import Link from "next/link";

function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between">
        <div className="mb-4 md:mb-0">
          <h4 className="text-lg font-semibold mb-2">Connect with Us</h4>
          <ul className="space-y-2">
            <li>
              <Link href="/discord" className="hover:underline">
                Discord
              </Link>
            </li>
            <li>
              <Link href="/twitter" className="hover:underline">
                Twitter
              </Link>
            </li>
            <li>
              <Link href="/github" className="hover:underline">
                GitHub
              </Link>
            </li>
            <li>
              <Link href="/linkedin" className="hover:underline">
                LinkedIn
              </Link>
            </li>
            <li>
              <Link href="/contact" className="hover:underline">
                Contact Us
              </Link>
            </li>
          </ul>
        </div>

        <div className="mb-4 md:mb-0">
          <h4 className="text-lg font-semibold mb-2">Our Services</h4>
          <ul className="space-y-2">
            <li>
              <Link href="/service1" className="hover:underline">
                Service 1
              </Link>
            </li>
            <li>
              <Link href="/service2" className="hover:underline">
                Service 2
              </Link>
            </li>
            <li>
              <Link href="/service3" className="hover:underline">
                Service 3
              </Link>
            </li>
          </ul>
        </div>

        <div className="mb-4 md:mb-0">
          <h4 className="text-lg font-semibold mb-2">Follow Us</h4>
          <div className="flex space-x-4">
            <span className="hover:text-gray-400 cursor-pointer">
              {/* Add icon here */}
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
                  d="M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z"
                />
              </svg>
            </span>
            <span className="hover:text-gray-400 cursor-pointer">
              {/* Add icon here */}
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
                  d="M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z"
                />
              </svg>
            </span>
            <span className="hover:text-gray-400 cursor-pointer">
              {/* Add icon here */}
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
                  d="M12 11c0-1.104-.896-2-2-2s-2 .896-2 2 .896 2 2 2 2-.896 2-2z"
                />
              </svg>
            </span>
            {/* Add more icons as needed */}
          </div>
        </div>
      </div>

      <div className="text-center mt-8 text-sm text-gray-400">
        © {new Date().getFullYear()} Your Company. All rights reserved.
      </div>
    </footer>
  );
}

export default Footer;