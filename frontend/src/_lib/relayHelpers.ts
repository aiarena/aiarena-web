// utils/relayHelpers.ts
export function nodes<T>(
  connection: { edges?: Array<{ node: T }> } | null | undefined,
): T[] {
  const edges = connection?.edges || [];
  return edges.map((edge) => edge.node);
}

// export const nodes = <T extends { node?: any }>(
//   connection: { readonly edges?: ReadonlyArray<T | null | undefined> | null | undefined } | null | undefined
// ): NonNullable<T['node']>[] => {
//   return (
//     connection?.edges
//       ?.map((edge) => edge?.node) // Extract nodes
//       .filter((node): node is NonNullable<T['node']> => Boolean(node)) || [] // Remove null/undefined nodes
//   );
// };

export function getNodes<T>(
  connection:
    | {
        readonly edges?: ReadonlyArray<
          | {
              readonly node: T | null | undefined;
            }
          | null
          | undefined
        >;
      }
    | null
    | undefined,
): T[] {
  return (
    connection?.edges
      ?.map((edge) => edge?.node) // Extract nodes
      .filter((node): node is T => node !== null && node !== undefined) || [] // Remove null/undefined nodes
  );
}
