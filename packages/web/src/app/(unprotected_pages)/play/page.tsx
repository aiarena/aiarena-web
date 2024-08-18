"use client";
import React from "react";



export default function Page() {


  return (
<div className="flex flex-col md:flex-row md:space-x-4">
    <div className="flex-1 bg-gray-700 p-6 mb-4 md:mb-0 md:mr-2">
      <h2 className="text-xl font-semibold mb-2">How to Get Started</h2>
      <p>Follow our comprehensive guide to build your first model and prepare it for competitive battling.</p>
    </div>
    
    <div className="flex-1 bg-gray-700 p-6">
      <h2 className="text-xl font-semibold mb-2">Already Have a Model?</h2>
      <p><span className="text-customGreen font-bold">Create an account</span> and start competing in the ladder to showcase your models prowess.</p>
    </div>
  </div>
  );
}
