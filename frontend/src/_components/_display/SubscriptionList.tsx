import React from "react";

type PlanAttributeKey =
  | "price"
  | "matchRequests"
  | "participants"
  | "star"
  | "discordRole";

const attributeLabels: Record<PlanAttributeKey, string> = {
  price: "Price",
  matchRequests: "Specific Match Requests",
  participants: "Active Participants",
  star: "Star",
  discordRole: "Discord Donator Role",
};

const SubscriptionComparisonTable = () => {
  const subscriptionPlans = [
    {
      tier: "Free",
      price: "Free",
      matchRequests: "10",
      participants: "3",
      star: "-",
      discordRole: "-",
    },
    {
      tier: "Bronze",
      price: "$60 /month",
      matchRequests: "80",
      participants: "3",
      star: "Bronze Star",
      discordRole: "Yes",
    },
    {
      tier: "Silver",
      price: "$115 /month",
      matchRequests: "200",
      participants: "8",
      star: "Silver Star",
      discordRole: "Yes",
    },
    {
      tier: "Gold",
      price: "$285 /month",
      matchRequests: "600",
      participants: "16",
      star: "Golden Star",
      discordRole: "Yes",
    },
    {
      tier: "Platinum",
      price: "$565 /month (plus VAT)",
      matchRequests: "2000",
      participants: "32",
      star: "Platinum Star",
      discordRole: "Yes",
    },
    {
      tier: "Diamond",
      price: "$1 125 /month (plus VAT)",
      matchRequests: "8000",
      participants: "Unlimited",
      star: "Diamond",
      discordRole: "Yes",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* For large screens */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full border-collapse border-gray-700 text-white">
          <thead>
            <tr className="h-12 bg-transparent">
              <th className="px-4 py-2"></th>
              {subscriptionPlans.map((plan, index) => (
                <th
                  key={plan.tier}
                  className={`px-4 py-2 text-center border border-transparent relative ${index === 2 ? "bg-transparent" : ""}`}
                >
                  {index === 2 && (
                    <span className="absolute top-1 left-1/2 transform -translate-x-1/2 bg-customGreen text-white font-bold text-sm px-2 py-1 rounded">
                      Most Popular
                    </span>
                  )}
                </th>
              ))}
            </tr>
            <tr>
              <th className="px-4 py-2"></th>
              {subscriptionPlans.map((plan) => (
                <th
                  key={plan.tier}
                  className="px-4 py-2 text-center border border-gray-700 bg-gray-800"
                >
                  {plan.tier}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.keys(attributeLabels).map((attribute) => (
              <tr key={attribute}>
                <td className="px-4 py-2 text-left font-semibold bg-gray-900">
                  {attributeLabels[attribute as PlanAttributeKey]}
                </td>
                {subscriptionPlans.map((plan) => (
                  <td
                    key={`${plan.tier}-${attribute}`}
                    className="px-4 py-2 text-center border border-gray-700"
                  >
                    {plan[attribute as PlanAttributeKey]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* For mobile screens */}
      <div className="md:hidden space-y-6">
        {subscriptionPlans.map((plan) => (
          <div
            key={plan.tier}
            className="border border-gray-700 rounded-lg p-4 bg-gray-800 text-white"
          >
            <h3 className="text-xl font-semibold mb-4">{plan.tier}</h3>
            {plan.tier === "Silver" && (
              <span className="block mb-4 text-center bg-customGreen text-white font-bold text-sm  py-1 rounded">
                Most Popular
              </span>
            )}
            <div className="space-y-2">
              <p>
                <span className="font-semibold">{attributeLabels.price}:</span> {plan.price}
              </p>
              <p>
                <span className="font-semibold">{attributeLabels.matchRequests}:</span>{" "}
                {plan.matchRequests}
              </p>
              <p>
                <span className="font-semibold">{attributeLabels.participants}:</span>{" "}
                {plan.participants}
              </p>
              <p>
                <span className="font-semibold">{attributeLabels.star}:</span> {plan.star}
              </p>
              <p>
                <span className="font-semibold">{attributeLabels.discordRole}:</span>{" "}
                {plan.discordRole}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionComparisonTable;
