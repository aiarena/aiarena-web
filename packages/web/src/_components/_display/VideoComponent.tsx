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
        <h1 className='mb-8'>AI Arena</h1>
        <h2 className='mb-8'>Compete with your AI models</h2>
        <div className='flex justify-around'>
          <button className='bg-black p-5'>Watch</button>
          <button className='bg-black p-5'>Play</button>
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