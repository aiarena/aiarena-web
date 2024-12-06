import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import Link from "next/link";

interface CompetitionCardProps {
  competition: {
    name: string;
    created: string;
    opened: string;
    status: string;
    progress: number;
    topPlayers: string[];
    participants: number;
    totalGames: number;
    imageUrl: string;
  };
}
export default function CompetitionCard({ competition }: CompetitionCardProps) {
  return (
    <Link
      href={`${getPublicPrefix()}/competitions/${1}`} // Assuming each competition has a unique ID or URL
      className="block bg-gray-900 text-white shadow-lg rounded-lg overflow-hidden hover:bg-gray-800 transition transform hover:scale-105"
    >
      <div className="flex">
        <div className="w-1/3">
        <Image
            width={411}
            height={231}
            src={competition.imageUrl}
            alt={competition.name}
            className="object-cover h-full"
            // style={{ height: '180px' }} // Adjusted height
          />
        </div>
        <div className="w-2/3 p-4 flex flex-col justify-between">
        <div className="flex justify-between">
          <h3 className="text-2xl font-bold mb-2 ml-0">{competition.name}</h3>
          <div className="pl-2 pb-2">
          <p>Total Games: {competition.totalGames}</p>
          <p className="mb-1">Bots: {competition.participants}</p>
         
          </div>
          </div>
  
         
          {/* <div className=" mb-2">
            <p className="mx-auto">Top Bots:</p>
            {competition.topPlayers.map((player, index) => (
              <span
                key={index}
                className="mr-2 cursor-pointer text-customGreen hover:text-white hover:underline transition"
                // onClick={() => console.log("hi")}
              >
                {player}
              </span>
            ))}
          </div> */}
         



         {/* Pretty good looking progress bar if we set a competition end date.  */}
          {/* <div className="mt-4">
            <div className="relative pt-1">
              <div className="flex justify-between">
            <p className="mb-1">Started: <br/> {competition.created}</p>
      
            <p className="mb-1">Ending: <br/> {competition.opened}</p>
            </div>
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-700">
                
                <div
                  style={{ width: `${competition.progress}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-customGreen"
                ></div>
              </div>
            </div>
          </div> */}
        </div>
      </div>
    </Link>
  );
}