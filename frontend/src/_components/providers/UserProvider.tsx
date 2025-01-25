
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

import {useUser} from "@/_components/_hooks/useUser";


// Define the shape of your User data
export interface User {
  id: string;
  username: string;
  email: string;
  patreonLevel?: string;
  dateJoined?: string;
  activeBotsLimit?: number,
  requestMatchesLimit?: number,
  requestMatchesCountLeft?: number,
}

// Define a context type
interface UserContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  fetching: boolean; // Add fetching state
}


const UserContext = createContext<UserContextType | undefined>(undefined);



// Create a provider component
export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [fetching, setFetching] = useState(true); // Initialize fetching to true

  // Fetch user data only once  
  const fetchedUser = useUser();

  // Update the user state if the data is fetched successfully
  useEffect(() => {
    if (fetchedUser) {
      setUser(fetchedUser); // Set the user data
      setFetching(false); // Set fetching to false after fetching is complete
    } else if (!fetchedUser) {
      setFetching(false); // If no user is fetched, set fetching to false
    }
    console.log(fetchedUser)
  }, [fetchedUser]);

  return (
    <UserContext.Provider value={{ user, setUser, fetching }}>
      {children}
    </UserContext.Provider>
  );
};

// Create a custom hook to access the user context
export const useUserContext = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUserContext must be used within a UserProvider');
  }
  return context;
};