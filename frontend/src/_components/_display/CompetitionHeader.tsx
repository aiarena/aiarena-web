import Image from "next/image";

interface CompetitionHeaderProps {
  name: string;
  imageUrl: string;
  status: string;
}

export default function CompetitionHeader({
  name,
  imageUrl,
  status,
}: CompetitionHeaderProps) {
  return (
    <div className="relative w-full h-36 md:h-36 lg:h-36">
      <Image
        src={imageUrl}
        alt={name}
        layout="fill"
        objectFit="cover"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="text-center text-white px-4">
          <h1 className="text-3xl md:text-5xl font-bold">{name}</h1>
          <p className="text-lg md:text-2xl mt-2"><b>Opened: </b>{status}</p>
        </div>
      </div>
    </div>
  );
}
