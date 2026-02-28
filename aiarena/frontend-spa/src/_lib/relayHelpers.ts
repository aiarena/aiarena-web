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

export function getIDFromBase64(
  base64Id: string | undefined | null,
  expectedType: string,
) {
  if (base64Id == null || base64Id == undefined || base64Id == "") {
    return null;
  }
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

export function getBase64FromID(id: string, type: string) {
  const raw = `${type}:${id}`;
  try {
    return btoa(raw);
  } catch (error) {
    console.error("Failed to encode Base64 ID:", error);
    return null;
  }
}