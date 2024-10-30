// utils/relayHelpers.ts
export function nodes<T>(connection: { edges?: Array<{ node: T }> } | null | undefined): T[] {
  const edges = connection?.edges || [];
  return edges.map(edge => edge.node);
}
