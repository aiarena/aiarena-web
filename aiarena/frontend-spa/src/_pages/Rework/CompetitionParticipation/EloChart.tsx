import { graphql, useFragment } from "react-relay";
import { EloChart_node$key } from "./__generated__/EloChart_node.graphql";
import { useEffect, useMemo } from "react";

import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import { Line } from "react-chartjs-2";
import "chartjs-adapter-date-fns";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  annotationPlugin
);

interface EloChartProps {
  data: EloChart_node$key;
}

export default function EloChart(props: EloChartProps) {
  const data = useFragment(
    graphql`
      fragment EloChart_node on CompetitionParticipationType {
        eloChartData {
          title
          lastUpdated
          data {
            datasets {
              label
              backgroundColor
              borderColor
              data {
                x
                y
              }
            }
          }
        }
      }
    `,
    props.data
  );

  const eloChart = data?.eloChartData;
  const dataset0 = eloChart?.data?.datasets?.[0];

  const chartData = useMemo(() => {
    if (!dataset0) return null;

    return {
      datasets: [
        {
          data: dataset0.data ?? [],
          borderColor: dataset0.borderColor ?? "#86c232",
          backgroundColor: dataset0.backgroundColor ?? "#86c232",
          pointRadius: 0,
          borderWidth: 2,
        },
      ],
    };
  }, [dataset0]);
  useEffect(() => {
    console.log(chartData);
  }, [chartData]);

  if (!chartData)
    return (
      <div className="rounded-xl border border-neutral-800 bg-darken-2 backdrop-blur-lg shadow-lg p-4 pt-8">
        <NoItemsInListMessage>
          <p>No match data available...</p>
        </NoItemsInListMessage>
      </div>
    );

  const lastUpdated =
    eloChart?.lastUpdated != null ? Number(eloChart.lastUpdated) : null;

  return (
    <div
      style={{ height: 558 }}
      className="rounded-xl border border-neutral-800 bg-darken-2 backdrop-blur-lg shadow-lg p-4 pt-8"
    >
      <Line
        data={chartData}
        options={{
          animation: false,
          responsive: true,
          maintainAspectRatio: false,

          scales: {
            x: {
              type: "time",
              time: { unit: "day" },
              ticks: { color: "#f3f4f6" },
              grid: { color: "rgba(134,194,50,0.15)" },
              title: { display: true, text: "Date", color: "#f3f4f6" },
            },
            y: {
              ticks: { color: "#f3f4f6" },
              grid: { color: "rgba(134,194,50,0.15)" },
              title: { display: true, text: "ELO", color: "#f3f4f6" },
            },
          },

          plugins: {
            datalabels: { display: false },
            legend: { display: false },
            tooltip: { mode: "index", intersect: false },
            annotation: {
              annotations: lastUpdated
                ? {
                    updatedLine: {
                      type: "line",
                      scaleID: "x",
                      value: lastUpdated,
                      borderColor: "rgba(243,244,246,0.65)",
                      borderWidth: 1,
                      borderDash: [6, 6],
                      label: {
                        display: true,
                        content: "Last updated",
                        position: "start",
                        yAdjust: 8,
                        backgroundColor: "rgba(0,0,0,0.6)",
                        color: "rgba(243,244,246,0.9)",
                        padding: 6,
                      },
                    },
                  }
                : {},
            },
          },

          interaction: { mode: "nearest", intersect: false },
        }}
      />
    </div>
  );
}
