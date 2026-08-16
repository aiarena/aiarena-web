export function formatDate(value: string | null | undefined) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleDateString();
}
