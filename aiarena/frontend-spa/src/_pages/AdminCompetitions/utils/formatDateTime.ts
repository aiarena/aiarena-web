export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString();
}
