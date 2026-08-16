import { formatDate } from "./formatDate";

export function DateValue({ value }: { value: string | null | undefined }) {
  return <>{formatDate(value)}</>;
}
