export type StatsPoint = {
  readonly dateTime: string;
  readonly count: number;
};

export type ChartPoint = {
  x: number;
  y: number;
};

export type DailyCounts = ReadonlyMap<number, number>;

export type StatsPeriod = "7d" | "30d" | "1y" | "all";

export const STATS_PERIODS: readonly {
  value: StatsPeriod;
  label: string;
  days: number | null;
  timeUnit: BucketUnit;
}[] = [
  { value: "7d", label: "Last 7 days", days: 7, timeUnit: "day" },
  { value: "30d", label: "Last 30 days", days: 30, timeUnit: "day" },
  { value: "1y", label: "Last year", days: 365, timeUnit: "month" },
  { value: "all", label: "All time", days: null, timeUnit: "month" },
];

export const DAY_IN_MS = 24 * 60 * 60 * 1000;

function toUtcDayTimestamp(value: string): number | null {
  const normalized = /^\d{4}-\d{2}-\d{2}$/.test(value)
    ? `${value}T00:00:00.000Z`
    : value;

  const date = new Date(normalized);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
}

export function toDailyCounts(
  points: readonly (StatsPoint | null | undefined)[],
): Map<number, number> {
  const counts = new Map<number, number>();

  for (const point of points) {
    if (!point) continue;
    const timestamp = toUtcDayTimestamp(point.dateTime);

    if (timestamp === null) {
      continue;
    }

    counts.set(timestamp, (counts.get(timestamp) ?? 0) + point.count);
  }

  return counts;
}

export function getTodayUtcTimestamp(): number {
  const now = new Date();

  return Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
}

/** Every UTC day from the earliest data point through today. */
export function createDailyDateRange(series: readonly DailyCounts[]): number[] {
  const timestamps = series.flatMap((counts) => Array.from(counts.keys()));

  if (!timestamps.length) {
    return [];
  }

  const firstDate = Math.min(...timestamps);
  const finalDate = Math.max(Math.max(...timestamps), getTodayUtcTimestamp());

  const dates: number[] = [];

  for (
    let timestamp = firstDate;
    timestamp <= finalDate;
    timestamp += DAY_IN_MS
  ) {
    dates.push(timestamp);
  }

  return dates;
}

/**
 * First UTC day included in the period (inclusive), or null for all time.
 * "Last 7 days" is today plus the 6 days before it.
 */
export function getPeriodStart(period: StatsPeriod): number | null {
  const days = STATS_PERIODS.find((p) => p.value === period)?.days ?? null;

  if (days === null) {
    return null;
  }

  return getTodayUtcTimestamp() - (days - 1) * DAY_IN_MS;
}

export function sumInPeriod(
  dailyCounts: DailyCounts,
  periodStart: number | null,
): number {
  let total = 0;

  for (const [date, count] of dailyCounts) {
    if (periodStart === null || date >= periodStart) {
      total += count;
    }
  }

  return total;
}

export function toCumulativeSeries(
  dates: readonly number[],
  dailyCounts: DailyCounts,
): ChartPoint[] {
  let total = 0;

  return dates.map((date) => {
    total += dailyCounts.get(date) ?? 0;

    return { x: date, y: total };
  });
}

export function toPercentageSeries(
  dates: readonly number[],
  numeratorDailyCounts: DailyCounts,
  denominatorDailyCounts: DailyCounts,
): ChartPoint[] {
  let numeratorTotal = 0;
  let denominatorTotal = 0;

  return dates.map((date) => {
    numeratorTotal += numeratorDailyCounts.get(date) ?? 0;
    denominatorTotal += denominatorDailyCounts.get(date) ?? 0;

    return {
      x: date,
      y: denominatorTotal > 0 ? (numeratorTotal / denominatorTotal) * 100 : 0,
    };
  });
}

/**
 * Cumulative series are computed over the full history so values stay true
 * totals; this only trims the visible window.
 */
export function clipToPeriod(
  series: readonly ChartPoint[],
  periodStart: number | null,
): ChartPoint[] {
  if (periodStart === null) {
    return [...series];
  }

  return series.filter((point) => point.x >= periodStart);
}

export const numberFormat = new Intl.NumberFormat();

export function formatPercent(numerator: number, denominator: number): string {
  return denominator > 0
    ? `${((numerator / denominator) * 100).toFixed(1)}%`
    : "–";
}

export function lineDataset(label: string, color: string, data: ChartPoint[]) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: color,
    pointRadius: 0,
    pointHoverRadius: 5,
    borderWidth: 2,
    stepped: "after" as const,
  };
}

export function stackedDataset(
  label: string,
  color: string,
  fillColor: string,
  data: ChartPoint[],
) {
  return {
    ...lineDataset(label, color, data),
    backgroundColor: fillColor,
    fill: true,
    stack: "stack",
  };
}

export type BucketUnit = "day" | "month" | "year";

function toBucketStart(timestamp: number, unit: BucketUnit): number {
  const date = new Date(timestamp);

  switch (unit) {
    case "day":
      return timestamp;
    case "month":
      return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1);
    case "year":
      return Date.UTC(date.getUTCFullYear(), 0, 1);
  }
}

function nextBucketStart(bucketStart: number, unit: BucketUnit): number {
  const date = new Date(bucketStart);

  switch (unit) {
    case "day":
      return bucketStart + DAY_IN_MS;
    case "month":
      return Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 1);
    case "year":
      return Date.UTC(date.getUTCFullYear() + 1, 0, 1);
  }
}

/**
 * Every bucket start from `start` through today, so empty days/months still
 * get a (zero) bar instead of the axis silently skipping them.
 */
export function createBuckets(start: number, unit: BucketUnit): number[] {
  const end = getTodayUtcTimestamp();
  const buckets: number[] = [];

  for (
    let bucket = toBucketStart(start, unit);
    bucket <= end;
    bucket = nextBucketStart(bucket, unit)
  ) {
    buckets.push(bucket);
  }

  return buckets;
}

/** Non-cumulative counts per bucket, for days on or after `periodStart`. */
export function toBucketedSeries(
  buckets: readonly number[],
  dailyCounts: DailyCounts,
  unit: BucketUnit,
  periodStart: number | null,
): ChartPoint[] {
  const totals = new Map<number, number>(buckets.map((b) => [b, 0]));

  for (const [date, count] of dailyCounts) {
    if (periodStart !== null && date < periodStart) continue;

    const bucket = toBucketStart(date, unit);
    if (totals.has(bucket)) {
      totals.set(bucket, (totals.get(bucket) ?? 0) + count);
    }
  }

  return buckets.map((bucket) => ({ x: bucket, y: totals.get(bucket) ?? 0 }));
}

export function barDataset(label: string, color: string, data: ChartPoint[]) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: color,
    borderRadius: 2,
    maxBarThickness: 24,
  };
}
