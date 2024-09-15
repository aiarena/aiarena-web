export const formatDate = (dateString: string, locale = 'en-GB') => {
  return new Date(dateString).toLocaleDateString(locale);
};
