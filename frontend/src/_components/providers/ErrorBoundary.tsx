"use client";

import React, { Component, ReactNode } from "react";

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

  handleRetry = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white p-3 rounded-lg shadow-md">
          <p>Something went wrong. Please refresh the page or try again.</p>
          <button
            onClick={this.handleRetry}
            className="mt-2 bg-white text-red-500 px-3 py-1 rounded-lg"
          >
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
