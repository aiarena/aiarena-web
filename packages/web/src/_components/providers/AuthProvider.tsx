

// 'use client'
// export const dynamic = 'force-dynamic'
// import handleError from '@/_lib/handleError';
// import React, {createContext, useContext, useState} from 'react';

// import { SessionProvider } from 'next-auth/react';
// type AuthProviderProps = {
//     children: React.ReactNode;
//   };

//   type AuthContextType = {
//     isLoggedIn: boolean;
//     setIsLoggedIn: React.Dispatch<React.SetStateAction<boolean>>;
//     authStatus: boolean;
//     setAuthStatus: React.Dispatch<React.SetStateAction<boolean>>;
//     status: string;
//     setStatus: React.Dispatch<React.SetStateAction<string>>;
//     authLoading: boolean;
//     setAuthLoading: React.Dispatch<React.SetStateAction<boolean>>;
//   };

// const AuthContext = createContext<AuthContextType | undefined>(undefined);

// const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
//     const [isLoggedIn, setIsLoggedIn] = useState(false);
//     const [authLoading, setAuthLoading] = useState(true);
//     const [authStatus, setAuthStatus] = useState(false);
//     const [status, setStatus ]  = useState('');

//     return (
//         <AuthContext.Provider value={{isLoggedIn, setIsLoggedIn, authLoading, setAuthLoading, authStatus, setAuthStatus, status, setStatus}}>
//             <SessionProvider>
//             {children}
//             </SessionProvider>
//         </AuthContext.Provider>
//     );
// }

// export function useAuth() {
//     const context = useContext(AuthContext);
//     if (!context) {
//         throw new Error("useAuth must be used within an AuthProvider");
//     }
//     return context;
// }

// export default AuthProvider;