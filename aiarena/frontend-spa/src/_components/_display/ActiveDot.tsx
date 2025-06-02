import { JSX } from "react";

const green = `
      .circular-gradient-shadow-green {
        width: 16px;
        height: 16px;
        position: relative;
        margin: 5px;
        border-radius: 50%;
        background: rgb(134, 254, 50);
        box-shadow: 0 0 1px rgba(134, 254, 50, 0.5);
        animation: rotate-gradient 4s linear infinite,
                   pulse          2s ease-in-out infinite;
      }

      .circular-gradient-shadow-green::before {
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
    `;

const blue = `
  .circular-gradient-shadow-blue {
    width: 16px;
    height: 16px;
    position: relative;
    margin: 5px;
    border-radius: 50%;
    background: rgb(50, 150, 254);
    box-shadow: 0 0 1px rgba(50, 150, 254, 0.5);
    
  .circular-gradient-shadow-blue::before {
    content: "";
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    border-radius: 50%;
    box-shadow: 0 0 1px rgba(50, 150, 254, 0.5);
    
  }
`;
const yellow = `
  .circular-gradient-shadow-yellow {
    width: 16px;
    height: 16px;
    position: relative;
    margin: 5px;
    border-radius: 50%;
    background: rgb(254, 230, 50);
    box-shadow: 0 0 1px rgba(254, 230, 50, 0.5);
    animation: rotate-gradient 4s linear infinite,
               pulse          2s ease-in-out infinite;
  }

  .circular-gradient-shadow-yellow::before {
    content: "";
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    border-radius: 50%;
    box-shadow: 0 0 1px rgba(254, 230, 50, 0.5);
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
    0%,100% { transform: scale(1);   box-shadow: 0 0 1px rgba(254,230,50,0.5); }
    50%     { transform: scale(1.1); box-shadow: 0 0 8px rgba(254,230,50,0.7); }
  }

  @keyframes pulse-shadow {
    0%,100% { box-shadow: 0 0 1px rgba(254,230,50,0.5); }
    50%     { box-shadow: 0 0 1px rgba(254,230,50,0.7); }
  }
`;

const gray = `
  .circular-gradient-shadow-gray {
    width: 16px;
    height: 16px;
    position: relative;
    margin: 5px;
    border-radius: 50%;
    background: rgb(160, 160, 160);
    box-shadow: 0 0 1px rgba(160, 160, 160, 0.5);
    
  }

  .circular-gradient-shadow-gray::before {
    content: "";
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    border-radius: 50%;
    box-shadow: 0 0 1px rgba(160, 160, 160, 0.5);
  }
`;

interface ActiveDotProps {
  color?: "green" | "blue" | "yellow" | "gray";
}

export default function ActiveDot({
  color = "green",
}: ActiveDotProps): JSX.Element {
  const styleMap = {
    green,
    blue,
    yellow,
    gray,
  };

  return (
    <>
      <style>{styleMap[color]}</style>
      <div className={`circular-gradient-shadow-${color}`} />
    </>
  );
}
