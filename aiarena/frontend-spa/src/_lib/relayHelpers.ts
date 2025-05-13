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


export function extractRelayID(base64Id: string, expectedType: string) {
    try {
        const decoded = atob(base64Id);
        const [type, id] = decoded.split(":");

        if (type === expectedType) {
            return id;
        } else {
            return null;
        }
    } catch (error) {
        console.error("Invalid Base64 ID:", error);
        return null;
    }
}