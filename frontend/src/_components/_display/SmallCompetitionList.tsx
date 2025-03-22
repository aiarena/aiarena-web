import { useState, useEffect } from 'react';
import { Competition } from '@/types';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

interface SmallCompetitionListProps {
  competitions: Competition[];
}

const getDivisionImage = (divisionNum: number): string => {
  switch (divisionNum) {
    case 1:
      return `${process.env.PUBLIC_PREFIX}/bot-icons/diamond.png`;
    case 2:
      return `${process.env.PUBLIC_PREFIX}/bot-icons/silver.png`;
    case 3:
      return `${process.env.PUBLIC_PREFIX}/bot-icons/bronze.png`;
    default:
      return `${process.env.PUBLIC_PREFIX}/bot-icons/bronze.png`;
  }
};


export default function SmallCompetitionList({ competitions }: SmallCompetitionListProps) {
  const [selectedCompetition, setSelectedCompetition] = useState<string | null>(null);
  const router = useRouter();
  useEffect(() => {
    if (competitions.length > 0) {
      setSelectedCompetition(competitions[0].node.name);
    }
  }, [competitions]);

  if (!selectedCompetition) {
    return <div className="text-center text-white">No competitions available.</div>;
  }

  const handleRowClick = (participantName: string) => {
    router.push(`/participant/${participantName}`);
  };

  return (
    <div className="mx-auto mt-8">
      <div className="flex justify-center space-x-4 mb-6">
        {competitions.map((competition, index) => (
          <button
            key={index}
            className={`px-4 py-2 font-semibold rounded-lg transition 
            ${selectedCompetition === competition.node.name ? 'bg-customGreen text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
            onClick={() => setSelectedCompetition(competition.node.name)}
          >
            {competition.node.name}
          </button>
        ))}
      </div>

      <div className="bg-gray-800 shadow rounded-lg p-6 text-white w-full">
  {competitions.map(
    (competition, index) =>
      selectedCompetition === competition.node.name && (
        <div key={index}>
          <h2 className="text-2xl font-bold mb-4 text-customGreen">{competition.node.name}</h2>
          <div className="overflow-hidden">
            <table className="w-full table-fixed text-left">
              <thead>
                <tr className="bg-gray-700">
                  <th className="px-4 py-2 truncate">Name</th>
                  <th className="px-4 py-2 truncate">Division</th>
                  <th className="px-4 py-2 truncate">Elo</th>
                  <th className="px-4 py-2 truncate">Trend</th>
                </tr>
              </thead>
              <tbody>
                {competition.node.participants.edges.map((participant, idx) => (
                  <tr
                    key={idx}
                    onClick={() => handleRowClick(participant.node.bot.name)}
                    className="border-t border-gray-600 hover:bg-gray-700 transition cursor-pointer"
                  >
                    <td className="px-4 py-2 font-semibold text-customGreen hover:text-white transition truncate">
                      {participant.node.bot.name}
                    </td>
                    <td className="px-4 py-2 flex items-center truncate">
                      <Image
                        width={40}
                        height={40}
                        src={getDivisionImage(participant.node.divisionNum)}
                        alt={`Division ${participant.node.divisionNum}`}
                        className="w-6 h-6 mr-2"
                      />
                    </td>
                    <td className="px-4 py-2 truncate">{participant.node.elo}</td>
                    <td className="px-4 py-2 truncate">{participant.node.trend}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )
  )}
</div>
    </div>
  );
}