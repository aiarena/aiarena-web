import { useSyncExternalStore } from "react";

// One app-wide 1-second clock. Every component showing a live duration reads
// from it, so a table with a hundred ticking cells runs a single interval and
// all of them tick in step, instead of a timer per cell drifting apart.
let now = Date.now();
let timer: ReturnType<typeof setInterval> | null = null;
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  if (timer === null) {
    // The clock sat idle while nobody listened; catch up before the first tick.
    now = Date.now();
    timer = setInterval(() => {
      now = Date.now();
      listeners.forEach((l) => l());
    }, 1000);
  }
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0 && timer !== null) {
      clearInterval(timer);
      timer = null;
    }
  };
}

const noopSubscribe = () => () => {};

/** The current time in ms, re-rendering every second while `enabled`. */
export default function useNow(enabled = true): number {
  return useSyncExternalStore(
    enabled ? subscribe : noopSubscribe,
    () => now,
  );
}
