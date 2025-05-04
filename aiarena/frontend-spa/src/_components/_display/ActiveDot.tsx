import React from "react";

const ActiveDot: React.FC = () => (
  <>
    <style>{`
      .circular-gradient-shadow {
        width: 16px;
        height: 16px;
        position: relative;
        margin: 5px auto;
        border-radius: 50%;
        background: rgb(134, 254, 50);
        box-shadow: 0 0 1px rgba(134, 254, 50, 0.5);
        animation: rotate-gradient 4s linear infinite,
                   pulse          2s ease-in-out infinite;
      }

      .circular-gradient-shadow::before {
        content: "";
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        border-radius: 50%;
        box-shadow: 0 0 1px rgba(134, 254, 50, 0.5);
        animation: rotate-shadow 4s linear infinite reverse,
                   pulse-shadow   4s ease-in-out infinite;
      }

      @keyframes rotate-gradient {
        0%   { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
      }

      @keyframes rotate-shadow {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }

      @keyframes pulse {
        0%,100% { transform: scale(1);   box-shadow: 0 0 1px rgba(134,254,50,0.5); }
        50%     { transform: scale(1.1); box-shadow: 0 0 8px rgba(134,254,50,0.7); }
      }

      @keyframes pulse-shadow {
        0%,100% { box-shadow: 0 0 1px rgba(134,254,50,0.5); }
        50%     { box-shadow: 0 0 1px rgba(134,254,50,0.7); }
      }

    `}</style>
    <div className="circular-gradient-shadow" />
  </>
);

export default ActiveDot;
