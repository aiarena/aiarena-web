import React from 'react';

const EthernetStatusDots: React.FC = () => {
  return (
    <div className="flex space-x-2">
      <div
        className="w-2 h-2 bg-orange-500 rounded-full"
        style={{
          animation: 'blinkOrange 1s infinite ease-in-out',
        }}
      ></div>
      <div
        className="w-2 h-2 bg-green-500 rounded-full"
        style={{
          animation: 'blinkGreen 0.5s infinite ease-in-out',
        }}
      ></div>
      <style jsx>{`
        @keyframes blinkOrange {
          0%, 20%, 50%, 70%, 100% {
            opacity: 1;
          }
          10%, 30%, 60%, 80% {
            opacity: 0;
          }
        }

        @keyframes blinkGreen {
          0%, 25%, 55%, 85%, 100% {
            opacity: 1;
          }
          15%, 35%, 75%, 90% {
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default EthernetStatusDots;