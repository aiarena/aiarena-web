export const getPublicPrefix = () => {
  let prefix = import.meta.env.BASE_URL;

  if (import.meta.env.DEV) {
    prefix = "http://localhost:4000/static/";
  }

  // Ensure there's no double trailing slash
  return prefix.slice(0, -1);
};
