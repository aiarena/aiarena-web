import { useState } from "react";

export default function useStateWithLocalStorage<T>(
  key: string,
  defaultValue: T | null = null,
): [T | null, (value: T | null) => void] {
  const [state, setState] = useState<T | null>(() => {
    const stored = sessionStorage.getItem(key);
    return stored != null ? (JSON.parse(stored) as T) : defaultValue;
  });

  const setStateWithLocalStorage = (value: T | null) => {
    setState(value);
    if (value == null) {
      sessionStorage.removeItem(key);
    } else {
      sessionStorage.setItem(key, JSON.stringify(value));
    }
  };

  return [state, setStateWithLocalStorage];
}
