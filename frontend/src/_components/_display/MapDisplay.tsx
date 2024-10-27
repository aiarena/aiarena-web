import Image from "next/image";

interface MapDisplayProps {
  mapName: string;
  imageUrl: string;
}

export default function MapDisplay({ mapName, imageUrl }: MapDisplayProps) {
  return (
    <div className="relative w-full h-full">
      <Image
        src={imageUrl}
        alt={mapName}
        layout="fill"
        objectFit="cover"
        className="object-cover rounded-lg"
      />
      <div className="absolute inset-0 flex items-center justify-center">
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black via-opacity-50 to-transparent"></div>
        {/* Centered Text */}
        <p className="relative text-white text-sm font-bold z-10">{mapName}</p>
      </div>
    </div>
  );
}
