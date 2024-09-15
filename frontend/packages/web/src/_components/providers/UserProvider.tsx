import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

import {useUser} from "@/_components/_hooks/useUser";


// Define the shape of your User data
export interface User {
  id: string;
  username: string;
  email: string;
   patreonLevel?: string;
  dateJoined?: string;
}

// Define a context type
interface UserContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);



// Create a provider component
export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  // Fetch user data only once
  const fetchedUser = useUser();

  // Update the user state if the data is fetched successfully
 useEffect(() => {
    if (!user && fetchedUser) {
      setUser(fetchedUser); // Only set user if it hasn't been set yet
    }
  }, [fetchedUser]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
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