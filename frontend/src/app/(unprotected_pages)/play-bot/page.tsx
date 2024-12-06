"use client"
import { useState } from "react";

const Page = () => {
  const [preferredLanguage, setPreferredLanguage] = useState("");
  const [preferredFramework, setPreferredFramework] = useState("");
  const [showTutorial, setShowTutorial] = useState(false);

  const handleLanguageSelection = (lang: string) => {
    setPreferredLanguage(lang);
    setPreferredFramework(""); // Reset framework selection when language changes
    setShowTutorial(false);
  };

  const handleFrameworkSelection = (framework: string) => {
    setPreferredFramework(framework);
    setShowTutorial(true);
  };

  return (
    <div className="min-h-screen bg-customBackgroundColor1 text-gray-200 p-6">
      some minimal py-sc2 install
    </div>
  );
};

export default Page;