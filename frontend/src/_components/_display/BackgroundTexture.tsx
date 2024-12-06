import { getPublicPrefix } from '@/_lib/getPublicPrefix';
import React, { FC, ReactNode } from 'react';


interface BackgroundTextureProps {
  children?: ReactNode;
  className?: string;
}

const BackgroundTexture: FC<BackgroundTextureProps> = ({ children, className = '' }) => {

  const style: React.CSSProperties = {
    backgroundImage: `url('${getPublicPrefix()}/backgrounds/background.gif')`,
    backgroundRepeat: 'repeat',
  };

  return (
    <div style={style} className={`${className}`}>
      {children}
    </div>
  );
};

export default BackgroundTexture;
