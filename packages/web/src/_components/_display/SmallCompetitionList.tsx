import { useState, useEffect } from 'react';
import { Competition } from '@/types';
import Link from 'next/link';

interface SmallCompetitionListProps {
  competitions: Competition[];
}

export default function SmallCompetitionList({ competitions }: SmallCompetitionListProps) {
  const [selectedCompetition, setSelectedCompetition] = useState<string | null>(null);

  useEffect(() => {
    if (competitions.length > 0) {
      setSelectedCompetition(competitions[0].node.name);
    }
  }, [competitions]);

  if (!selectedCompetition) {
    return <div className="text-center text-white">No competitions available.</div>;
  }

  return (
    <div className="max-w-2xl mx-auto mt-8">
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

      <div className="bg-gray-800 shadow rounded-lg p-6 text-white">
        {competitions.map(
          (competition, index) =>
            selectedCompetition === competition.node.name && (
              <div key={index}>
                <h2 className="text-2xl font-bold mb-4 text-customGreen">{competition.node.name}</h2>
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-gray-700">
                      <th className="px-4 py-2">Name</th>
                      <th className="px-4 py-2">Division</th>
                      <th className="px-4 py-2">Elo</th>
                      <th className="px-4 py-2">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competition.node.participants.edges.map((participant, idx) => (
                      <tr
                        key={idx}
                        className="border-t border-gray-600 hover:bg-gray-700 transition cursor-pointer"
                      >
                        <td className="px-4 py-2 font-semibold text-customGreen hover:text-white transition">
                          <Link href={`/participant/${participant.node.bot.name}`}>
                            {participant.node.bot.name}
                          </Link>
                        </td>
                        <td className="px-4 py-2">{participant.node.divisionNum}</td>
                        <td className="px-4 py-2">{participant.node.elo}</td>
                        <td className="px-4 py-2">{participant.node.trend}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
        )}
      </div>
    </div>
  );
}
