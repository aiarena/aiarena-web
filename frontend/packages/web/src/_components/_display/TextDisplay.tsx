import React from 'react';
import { useSecureFetchText } from '@/_components/_hooks/useSecureFetchText';

interface TextDisplayProps {
    path: string;
  }

  const TextDisplay: React.FC<TextDisplayProps> = ({ path }) => {
    
    const { data, isLoading, error } = useSecureFetchText(path);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return <div>{data}</div>; // Display the fetched text
};

export default TextDisplay;