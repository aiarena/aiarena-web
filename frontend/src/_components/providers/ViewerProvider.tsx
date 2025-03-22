import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { Viewer, useViewer } from "@/_components/_hooks/useViewer";

// Define a context type
interface ViewerContextType {
  viewer: Viewer | null;
  setViewer: React.Dispatch<React.SetStateAction<Viewer | null>>;
  fetching: boolean; // Add fetching state
}

const ViewerContext = createContext<ViewerContextType | undefined>(undefined);

// Create a provider component
export const ViewerProvider = ({ children }: { children: ReactNode }) => {
  const [viewer, setViewer] = useState<Viewer | null>(null);
  const [fetching, setFetching] = useState(true); // Initialize fetching to true

  // Fetch user data only once
  const fetchedViewer = useViewer();

  // Update the user state if the data is fetched successfully
  useEffect(() => {
    if (fetchedViewer) {
      setViewer(fetchedViewer);
    }
    setFetching(false);
  }, [fetchedViewer]);

  return (
    <ViewerContext.Provider value={{ viewer: viewer, setViewer, fetching }}>
      {children}
    </ViewerContext.Provider>
  );
};

// Create a custom hook to access the user context
export const useViewerContext = (): ViewerContextType => {
  const context = useContext(ViewerContext);
  if (!context) {
    throw new Error("useViewerContext must be used within a UserProvider");
  }
  return context;
};
