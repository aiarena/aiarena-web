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
import { graphql, useFragment } from "react-relay";
import ChartDataLabels from "chartjs-plugin-datalabels";
import { WinsByTime_node$key } from "./__generated__/WinsByTime_node.graphql";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ChartDataLabels
);
interface WinsByTimeProps {
  data: WinsByTime_node$key;
}
export default function WinsByTime(props: WinsByTimeProps) {
  const data = useFragment(
    graphql`
      fragment WinsByTime_node on CompetitionParticipationType {
        winrateChartData {
          title
          data {
            labels
            datasets {
              label
              data
              backgroundColor
              extraLabels
            }
          }
        }
      }
    `,
    props.data
  );

  const winrateChart = data?.winrateChartData;
  if (!winrateChart) return null;

  const labels = winrateChart.data?.labels;
  const datasets = winrateChart.data?.datasets;

  if (!labels || !datasets) return null;

  const labelsMutable = [...labels];
  return (
    <div
      style={{ height: 400 }}
      className="bg-darken-2 rounded-2xl shadow-2xl p-4 pt-8 border border-neutral-700"
    >
      <Bar
        data={{
          labels: labelsMutable,
          datasets: datasets.map((ds) => ({
            label: ds?.label,
            data: ds?.data,
            backgroundColor: ds?.backgroundColor,

            stack: "stack1",
          })),
        }}
        options={{
          animation: false,
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              ticks: { color: "#f3f4f6" },
              title: {
                display: true,
                text: "Match duration (min)",
                color: "#f3f4f6",
              },
            },
            y: {
              stacked: true,
              ticks: { color: "#f3f4f6" },
              title: { display: true, text: "Games", color: "#f3f4f6" },
              beginAtZero: true,
            },
          },
          plugins: {
            legend: { display: true },
            tooltip: {
              callbacks: {
                title: (items) => {
                  const label = items[0]?.label;
                  return label ? `${label} minutes` : "";
                },
                label: (context: TooltipItem<"bar">) => {
                  const ds = datasets[context.datasetIndex];
                  const pct = ds?.extraLabels?.[context.dataIndex];
                  const val = context.parsed.y;

                  return pct
                    ? `${context.dataset.label}: ${val} (${pct})`
                    : `${context.dataset.label}: ${val}`;
                },
              },
            },
            datalabels: {
              color: "#f3f4f6",
              anchor: "center",
              align: "center",
              formatter: (value: number) => {
                return value > 0 ? value : "";
              },
              font: {
                weight: "bold",
                size: 12,
              },
            },
          },
        }}
      />
    </div>
  );
}
