"use client";

import React, { Component, ReactNode } from "react";
import MainButton from "../_props/MainButton";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

export default class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <>
          <div className=" h-[100vh] w-[100vw] text-white flex justify-center items-center filter:darken bg-darken">
            <div>
              <div className="pb-8">
                <h2 className="pb-8">Something went wrong.</h2>

                <MainButton
                  onClick={() => {
                    window.location.href = "/";
                  }}
                  text="Home"
                />
              </div>
              <div>
                <h4 className="pb-4"> Or use the old frontend</h4>

                <MainButton
                  onClick={() => {
                    window.location.href = "/old-frontend/";
                  }}
                  text="Old Frontend"
                />
              </div>
            </div>
          </div>
          <div className="fixed left-4 sm:left-auto bottom-4 right-4 bg-red-500 text-white p-3 rounded-lg shadow-md">
            <p>Something went wrong.</p>
          </div>
        </>
      );
    }

    return this.props.children;
  }
}
