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

/**
 * Decode a Relay global id to its raw database id, asserting the node type.
 *
 * The return type mirrors the input's nullability: a non-null id in yields a
 * `string` out, a possibly-absent id yields `string | null`. So an absent id —
 * the one thing that legitimately varies at runtime (the GraphQL field was
 * itself null) — is surfaced to the caller to handle, while a present id needs
 * no guard.
 *
 * The other two ways decoding can fail — malformed base64, or a node type that
 * doesn't match `expectedType` — mean the wrong field or the wrong type literal
 * was wired up. That's a programming error, not runtime data, so it throws
 * loudly rather than returning null and widening the type for everyone.
 */
export function getIDFromBase64(base64Id: string, expectedType: string): string;
export function getIDFromBase64(
  base64Id: string | undefined | null,
  expectedType: string,
): string | null;
export function getIDFromBase64(
  base64Id: string | undefined | null,
  expectedType: string,
): string | null {
  if (base64Id == null || base64Id === "") {
    return null;
  }

  let decoded: string;
  try {
    decoded = atob(base64Id);
  } catch {
    throw new Error(`Invalid Base64 ID: ${base64Id}`);
  }

  const [type, id] = decoded.split(":");
  if (type !== expectedType) {
    throw new Error(`Expected a ${expectedType} global id, got ${type}`);
  }
  return id;
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