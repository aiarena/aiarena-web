import React from "react";

const PricingCard: React.FC<{
  plan: string;
  price: string;
  features: string[];
  isPopular?: boolean;
}> = ({ plan, price, features, isPopular = false }) => {
  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 text-center border-t-4 ${
        isPopular ? "border-green-500" : "border-transparent"
      } hover:shadow-lg transition-shadow duration-300`}
    >
      {isPopular && (
        <div className="absolute top-0 right-0 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-bl-lg">
          Popular
        </div>
      )}
      <h3 className="text-2xl font-bold mb-4">{plan}</h3>
      <div className="text-4xl font-extrabold mb-4">{price}</div>
      <ul className="text-gray-600 mb-6 space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center justify-center">
            <span className="mr-2">✔</span> {feature}
          </li>
        ))}
      </ul>
      <button className="bg-green-500 text-white py-2 px-4 rounded-full hover:bg-green-600 transition-colors duration-300">
        Choose Plan
      </button>
    </div>
  );
};

export default PricingCard;
