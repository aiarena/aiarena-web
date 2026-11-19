import {
  ChartData,
  Chart as ChartJS,
  ChartOptions,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  TimeScale,
  Tooltip,
  TooltipItem,
} from "chart.js";
import { Line } from "react-chartjs-2";
import "chartjs-adapter-date-fns";

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
);

export type StatsTotalCard = {
  label: string;
  value: string;
  detail: string;
  color: string;
};

interface AdminStatsChartSectionProps {
  description?: string;
  cards: readonly StatsTotalCard[];
  data: ChartData<"line", { x: number; y: number }[]>;
  timeUnit: "day" | "month" | "year";
  yTitle: string;
  gridColor: string;
  stacked?: boolean;
  yMax?: number;
  formatTick?: (value: number | string) => string;
  formatTooltipLabel?: (item: TooltipItem<"line">) => string;
  formatTooltipFooter?: (items: TooltipItem<"line">[]) => string;
}

const TEXT_COLOR = "#f3f4f6";

function TotalCard({ card }: { card: StatsTotalCard }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-darken-2 px-4 py-3 shadow-lg backdrop-blur-lg">
      <div className="flex items-center gap-2 text-xs text-neutral-400">
        <span
          className="inline-block size-2 shrink-0 rounded-full"
          style={{ backgroundColor: card.color }}
        />
        <span className="truncate">{card.label}</span>
      </div>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-neutral-100">
        {card.value}
      </p>
      <p className="truncate text-xs text-neutral-500">{card.detail}</p>
    </div>
  );
}

export default function AdminStatsChartSection(
  props: AdminStatsChartSectionProps,
) {
  const options: ChartOptions<"line"> = {
    animation: false,
    responsive: true,
    maintainAspectRatio: false,
    parsing: false,
    normalized: true,
    interaction: {
      mode: "nearest",
      axis: "x",
      intersect: false,
    },
    scales: {
      x: {
        type: "time",
        stacked: props.stacked,
        time: {
          unit: props.timeUnit,
          tooltipFormat: "PP",
        },
        ticks: {
          color: TEXT_COLOR,
          maxRotation: 0,
          autoSkip: true,
        },
        grid: { color: props.gridColor },
        title: { display: true, text: "Date", color: TEXT_COLOR },
      },
      y: {
        beginAtZero: true,
        stacked: props.stacked,
        max: props.yMax,
        ticks: {
          color: TEXT_COLOR,
          precision: 0,
          callback: props.formatTick,
        },
        grid: { color: props.gridColor },
        title: { display: true, text: props.yTitle, color: TEXT_COLOR },
      },
    },
    plugins: {
      datalabels: { display: false },
      legend: {
        display: true,
        labels: {
          color: TEXT_COLOR,
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        mode: "index",
        intersect: false,
        callbacks: {
          label: props.formatTooltipLabel,
          footer: props.formatTooltipFooter,
        },
      },
    },
  };

  return (
    <div className="flex flex-col gap-4">
      {props.description && (
        <p className="text-sm text-neutral-400">{props.description}</p>
      )}

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {props.cards.map((card) => (
          <TotalCard key={card.label} card={card} />
        ))}
      </div>

      <div
        className="rounded-xl border border-neutral-800 bg-darken-2 p-4 pt-6 shadow-lg backdrop-blur-lg"
        style={{ height: 558 }}
      >
        <Line data={props.data} options={options} />
      </div>
    </div>
  );
}
