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
