import Link from "next/link";

interface ClosedCompetition {
  name: string;
  created: string;
  opened: string;
  closed: string;
}

interface ClosedCompetitionListProps {
  competitions: ClosedCompetition[];
}
export default function ClosedCompetitionList({ competitions }: ClosedCompetitionListProps) {
  return (
    <ul className="text-white">
      {competitions.map((comp, index) => (
        <li key={index} className="mb-2">
          <Link
            href={`/competition/${index}`} // Assuming each competition has a unique ID or URL
            className="block p-2 hover:bg-gray-700 rounded transition"
          >
            <span className="font-bold">{comp.name}</span> 
            <span className="ml-2 text-sm text-gray-400">Created: {comp.created}</span>
            <span className="ml-2 text-sm text-gray-400">Opened: {comp.opened}</span>
            <span className="ml-2 text-sm text-gray-400">Closed: {comp.closed}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}