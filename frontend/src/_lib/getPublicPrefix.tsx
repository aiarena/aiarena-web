export const getPublicPrefix = () => {
    const prefix = process.env.PUBLIC_PREFIX || '';
    // Check if it's a relative URL (not starting with http)
    if (!prefix.startsWith('https')) {
      // Ensure the prefix starts with a slash for relative paths in dev
      return prefix.startsWith('/') ? prefix : `/${prefix}`;
    }
    return prefix as string; // Return as is for production (absolute URLs)
  };