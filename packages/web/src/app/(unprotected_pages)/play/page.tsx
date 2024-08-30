"use client";
import Image from "next/image";
import { useRouter } from "next/navigation";
import React from "react";


export default function Page() {
  const router = useRouter();

  const handleRedirect = (path: string) => {
    router.push(path);
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] ">
      <div className="flex flex-col md:flex-row md:space-x-4">
        
        {/* First Box */}
        <div className="flex flex-col flex-1 bg-gray-700 p-6 rounded-lg shadow-lg relative overflow-hidden m-8">
          {/* Image Section */}
          <div className="mb-4 relative">
            <Image
              alt="How to Get Started"
              src="/demo_assets/adj_1_1.png"
              height={500}
              width={500}
              className="w-full h-auto rounded-lg"
            />
            <h2 className="text-xl font-semibold text-white absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/4 bg-customGreen bg-opacity-90 px-4 py-1 rounded-md shadow-lg">
              How to Get Started
            </h2>
          </div>
          
          <div className="flex-grow mt-6">
            <p className="text-gray-300 mb-4">Follow our comprehensive guide to build your first model and prepare it for competitive battling.</p>
          </div>
          <div className="mt-4">
            <button
              onClick={() => handleRedirect('/watch')}
              className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
            >
              Build your first model
            </button>
            <button
              onClick={() => handleRedirect('/watch')}
              className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
            >
              Quickstart
            </button>
          </div>
          <p>Super important to show that donating gives you more playtime.</p>
        </div>
        
        {/* Second Box */}
        <div className="flex flex-col flex-1 bg-gray-700 p-6 rounded-lg shadow-lg relative overflow-hidden m-8">
          {/* Image Section */}
          <div className="mb-4 relative">
            <Image
              alt="Already Have a Model?"
              src="/demo_assets/adj_2_1.png"
              height={500}
              width={500}
              className="w-full h-auto rounded-lg"
            />
            <h2 className="text-xl font-semibold text-white absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/4 bg-customGreen bg-opacity-90 px-4 py-1 rounded-md shadow-lg">
              Already Have a Model?
            </h2>
          </div>
          
          <div className="flex-grow mt-6">
            <p className="text-gray-300 mb-4">Create an account and start competing in the ladder to showcase your model&apos;s prowess.</p>
          </div>
          <div className="mt-4">
            <button
              onClick={() => handleRedirect('/watch')}
              className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
            >
              Create account
            </button>
          </div>
        </div>
        
      </div>
    </div>
  );
}
