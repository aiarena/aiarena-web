"use client"
import { useUser } from '@/_components/_hooks/useUser'; // Assuming your hook is here
import { useSignOut } from '@/_components/_hooks/useSignOut'; // Assuming your hook is here
import { useRouter } from 'next/navigation';
import {useUserContext} from "@/_components/providers/UserProvider";
import { useEffect, useState } from "react";
import TabNavigation from '@/_components/_nav/TabNav';
import BotOverview from '@/_components/_display/BotOverview';

export default function Page() {

  const [signOut, isSigningOut] = useSignOut(); // SignOut mutation and loading state
  const router = useRouter(); // Next.js router for navigation
    const {user, setUser, fetching } = useUserContext()

  // Handle sign out and redirect
  const handleSignOut = () => {
    signOut(); // Trigger the sign out mutation
      setUser(null);
    router.push("/"); // Redirect to /profile after sign out
  };

  useEffect(() => {
    if(user === null && fetching == false) {
      router.push("/");
    }
    console.log(user, fetching)    
  }, [user, fetching, router])
  

  // <p>Logged in as {user?.id}</p>
  // <button onClick={handleSignOut} disabled={isSigningOut} className={"bg-red-500"}>
  //   {isSigningOut ? "Signing Out..." : "Log Out"}
  // </button>


  return (
    <div className="min-h-screen bg-gray-800">
      <div className=" mx-auto py-8 px-4">

        {/* Navigation Tabs */}
        <TabNavigation
          tabs={[
            { name: 'Bots', href: '', active: true },
            { name: 'Achievements', href: '#competition-table' },
            { name: 'Settings', href: '#settings' },
          ]}
        />

        {/* Bot Overview Section */}
        <div id="bot-overview" className="mt-8">
          <BotOverview/>
        </div>

        {/* Competition Table Section */}
        {/* <div id="competition-table" className="mt-8">
          <CompetitionTable />
        </div> */}
      </div>
    </div>
  );
};