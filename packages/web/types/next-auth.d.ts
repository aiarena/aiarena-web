import NextAuth from "next-auth"

declare module "next-auth" {
  /**
   * Returned by `useSession`, `getSession` and received as a prop on the `SessionProvider` React Context
   */

  interface User {
   
        refreshToken: string;
        token: string;
        authError: boolean;
        newUser?: boolean;
        id?: string;
    

  }
  interface Session {
    signOut: boolean;
    user: {
      /** The user's postal address. */
      
      address: string
    }
  }
}