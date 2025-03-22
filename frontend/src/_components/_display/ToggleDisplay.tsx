import { useState } from "react";

interface ToggleDisplayProps {
  rankings: JSX.Element;
  rounds: JSX.Element;
}

export default function ToggleDisplay({
  rankings,
  rounds,
}: ToggleDisplayProps) {
  const [activeTab, setActiveTab] = useState<"rankings" | "rounds">("rankings");

  return (
    <div className="mt-8">
      <div className="flex justify-center space-x-4 mb-6">
        <button
          className={`px-4 py-2 font-semibold rounded-lg transition ${
            activeTab === "rankings"
              ? "bg-customGreen text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
          onClick={() => setActiveTab("rankings")}
        >
          Rankings
        </button>
        <button
          className={`px-4 py-2 font-semibold rounded-lg transition ${
            activeTab === "rounds"
              ? "bg-customGreen text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
          onClick={() => setActiveTab("rounds")}
        >
          Rounds
        </button>
      </div>

      <div>
        {activeTab === "rankings" && rankings}
        {activeTab === "rounds" && rounds}
      </div>
    </div>
  );
}
