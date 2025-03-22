export const getPublicPrefix = () => {
  const prefix = process.env.PUBLIC_PREFIX || "";

  // Handle the development environment where prefix is `.`
  if (prefix === ".") {
    return "";
  }

  // Ensure there's no double leading slash
  return prefix.startsWith("/") ? prefix : `/${prefix}`;
};
