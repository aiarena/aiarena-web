import React from "react";

interface Player {
  rank: number;
  race: string;
  name: string;
  division: number;
  elo: number;
}

interface PlayerRankingListProps {
  players: Player[];
}

const PlayerRankingList: React.FC<PlayerRankingListProps> = ({ players }) => {
  return (
    <div className="overflow-x-auto w-full">
       <h3 className="text-lg font-bold mb-2">Starcraft Rankings</h3>
      <table className="min-w-full table-auto">
        <thead>
          <tr>
            <th className="px-4 py-2">Rank</th>
            <th className="px-4 py-2">Race</th>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Div</th>
            <th className="px-4 py-2">Elo</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player) => (
            <tr key={player.rank}>
              <td className="border px-4 py-2">{player.rank}</td>
              <td className="border px-4 py-2">{player.race}</td>
              <td className="border px-4 py-2">{player.name}</td>
              <td className="border px-4 py-2">{player.division}</td>
              <td className="border px-4 py-2">{player.elo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PlayerRankingList;