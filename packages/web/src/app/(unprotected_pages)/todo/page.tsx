"use client"

import React from "react";


const ToDoPage: React.FC = () => {
  return (
  <>
    <div className="container mx-auto py-8">
        <h1>Todo</h1>

        <ul>
          <li>
            <p>-There has to be a way to bypass the twitch commercial.</p>
          </li>
          <li>
            <p>- Implement SSR & GQL db</p>
          </li>
          <li>
          <p>- Adding content shift guards for hydrated content</p>
          </li>

        </ul>
 </div>
     </>
  );
};

export default ToDoPage;
