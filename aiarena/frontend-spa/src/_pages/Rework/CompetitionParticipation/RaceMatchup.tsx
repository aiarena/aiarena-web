import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  TooltipItem,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import ChartDataLabels from "chartjs-plugin-datalabels";
import { graphql, useFragment } from "react-relay";
import { RaceMatchup_node$key } from "./__generated__/RaceMatchup_node.graphql";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ChartDataLabels
);

interface RaceMatchupChartProps {
  data: RaceMatchup_node$key;
}

export default function RaceMatchup(props: RaceMatchupChartProps) {
  const node = useFragment(
    graphql`
      fragment RaceMatchup_node on CompetitionParticipationType {
        raceMatchup {
          zerg {
            wins
            losses
            ties
            crashes
            played
            winRate
            lossRate
            tieRate
            crashRate
          }
          protoss {
            wins
            losses
            ties
            crashes
            played
            winRate
            lossRate
            tieRate
            crashRate
          }
          terran {
            wins
            losses
            ties
            crashes
            played
            winRate
            lossRate
            tieRate
            crashRate
          }
          random {
            wins
            losses
            ties
            crashes
            played
            winRate
            lossRate
            tieRate
            crashRate
          }
        }
      }
    `,
    props.data
  );

  const noItemsMessage = (
    <NoItemsInListMessage>
      <p>No match data available...</p>
    </NoItemsInListMessage>
  );

  const matchup = node?.raceMatchup;
  if (!matchup) return noItemsMessage;

  const labels = ["Zerg", "Protoss", "Terran", "Random"] as const;

  const races = [
    matchup.zerg,
    matchup.protoss,
    matchup.terran,
    matchup.random,
  ] as const;

  const totalPlayed = races.reduce((sum, r) => sum + r.played, 0);
  if (totalPlayed === 0) return noItemsMessage;

  return (
    <div
      style={{ height: 400 }}
      className="bg-darken-2 rounded-2xl shadow-2xl p-4 pt-8 border border-neutral-700"
    >
      <Bar
        data={{
          labels: [...labels],
          datasets: [
            {
              label: "Wins",
              data: races.map((r) => r.winRate),
              backgroundColor: "#86C232",
              stack: "stack1",
            },
            {
              label: "Losses",
              data: races.map((r) => r.lossRate),
              backgroundColor: "#D20044",
              stack: "stack1",
            },
            {
              label: "Ties",
              data: races.map((r) => r.tieRate),
              backgroundColor: "#DFCE00",
              stack: "stack1",
            },
            {
              label: "Crashes",
              data: races.map((r) => r.crashRate),
              backgroundColor: "#AAAAAA",
              stack: "stack1",
            },
          ],
        }}
        options={{
          animation: false,
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              ticks: { color: "#f3f4f6" },
              title: { display: true, text: "Opponent race", color: "#f3f4f6" },
              grid: { color: "rgba(243,244,246,0.08)" },
            },
            y: {
              stacked: true,
              min: 0,
              max: 100,
              ticks: {
                color: "#f3f4f6",
                callback: (value) => `${value}%`,
              },
              title: { display: true, text: "Rate", color: "#f3f4f6" },
              grid: { color: "rgba(243,244,246,0.08)" },
            },
          },
          plugins: {
            legend: {
              display: true,
              labels: { color: "#f3f4f6" },
            },
            tooltip: {
              callbacks: {
                title: (items) => items[0]?.label ?? "",
                label: (context: TooltipItem<"bar">) => {
                  const race = races[context.dataIndex];
                  const v = context.parsed.y;

                  let count = 0;
                  if (context.dataset.label === "Wins") count = race.wins;
                  if (context.dataset.label === "Losses") count = race.losses;
                  if (context.dataset.label === "Ties") count = race.ties;
                  if (context.dataset.label === "Crashes") count = race.crashes;

                  return `${context.dataset.label}: ${count}/${race.played} (${v?.toFixed(
                    2
                  )}%)`;
                },
              },
            },
            datalabels: {
              color: "#f3f4f6",
              anchor: "center",
              align: "center",
              formatter: (value: number) =>
                value > 0 ? `${Math.round(value)}%` : "",
              font: { weight: "bold", size: 12 },
            },
          },
        }}
      />
    </div>
  );
}
