import React from 'react';

const VideoComponent = ({source} : {source : string}) => {
  return (
    <div style={{ width: '100%', height: '75vh', overflow: 'hidden' }}>
      <video
        src={source} // Replace this with the path to your video
        autoPlay
        loop
        muted
        playsInline
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
      {/* Overlay content */}
      <div style={{
        position: 'absolute',
        top: '40%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
        color: 'white', // Adjust based on your design
      }}>
        <h1 style={{ marginBottom: '20px' }}>AI Arena</h1>
        <h1 style={{ marginBottom: '20px' }}>Compete with your AI models</h1>
        <div>
          <button style={buttonStyle}>Watch</button>
          <button style={buttonStyle}>Play</button>
        </div>
      </div>
    </div>
  );
};

// Inline style for buttons
const buttonStyle = {
  margin: '10px',
  padding: '10px 20px',
  fontSize: '16px',
  color: 'white',
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  outline: 'none',
  transition: 'background-color 0.3s',
};

export default VideoComponent;