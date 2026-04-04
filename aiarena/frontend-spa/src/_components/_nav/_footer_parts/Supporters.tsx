import React, { Suspense } from "react";

import { Link } from "react-router";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import RandomSupporter from "@/_components/_display/RandomSupporter";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

const SupportersComponent: React.FC = () => {
  return (
    <div className="mb-16 px-8 text-center flex-1 mx-auto">
      <WrappedTitle title="Funded by You" />
      <div className="justify-center flex">
        <Suspense fallback={<LoadingSpinner />}>
          <ErrorBoundaryWrapper componentName="random supporter">
            <RandomSupporter />
          </ErrorBoundaryWrapper>
        </Suspense>
      </div>

      <p className="text-lg mb-6">
        Thank you for your support! <br /> Your <a href="https://www.patreon.com/aiarena" target="_blank" rel="noopener noreferrer" className="text-customGreen hover:text-white transition">
          Patreon
        </a> contributions help us keep
        going.
      </p>
      <div className="flex justify-center">
        <Link
          to="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit?gid=1303247903#gid=1303247903"
          target="_blank"
        >
          <div className="flex items-center">
            <img
              alt="Excel-Icon"
              src={`${getPublicPrefix()}/icons/excel-icon.svg`}
              height={35}
              width={35}
              className="pr-2"
            />
            <p className="text-customGreen text-lg hover:text-white transition">
              Project Finance
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default SupportersComponent;
