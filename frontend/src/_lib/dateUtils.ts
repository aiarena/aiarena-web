// For displaying data to users
export const formatDate = (dateString: string, locale = 'en-GB') => {
  return new Date(dateString).toLocaleDateString(locale);
};


// For internal uses
export const formatDateISO = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toISOString().replace("T", " ").slice(0, 19); // YYYY-MM-DD HH:mm:ss
  };
