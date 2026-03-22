import React, { Component, ReactNode } from "react";
import { ProviderContext, useSnackbar } from "notistack";

interface ErrorBoundaryProps {
  children: ReactNode;

  enqueueSnackbar: ProviderContext["enqueueSnackbar"];
  override?: string;
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    this.setState({ error });
    console.error("Error caught by ErrorBoundary:", error, info);

    this.props.enqueueSnackbar(error.toString(), { variant: "error" });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <span className="flex justify-center align-middle text-red-500">
            {this.props.override ||
              this?.state?.error?.toString() ||
              "Server Error"}
          </span>
          {this.props.componentName && (
            <span className="flex justify-center align-middle text-red-500">
              Unable to load {this.props.componentName}
            </span>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

const ErrorBoundaryWrapper: React.FC<{
  children: ReactNode;
  override?: string;
  componentName?: string;
}> = ({ children, override, componentName }) => {
  const { enqueueSnackbar } = useSnackbar();

  return (
    <ErrorBoundary
      enqueueSnackbar={enqueueSnackbar}
      override={override}
      componentName={componentName}
    >
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundaryWrapper;
