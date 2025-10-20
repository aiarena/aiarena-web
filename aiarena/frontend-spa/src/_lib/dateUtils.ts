// For displaying data to users
export const getDateToLocale = (dateString: string, locale = "en-GB") => {
  if (!dateString) {
    return "";
  }

  if (dateString.trim() == "") {
    return "";
  }

  try {
    return new Date(dateString).toLocaleDateString(locale) || "";
  } catch {
    return "";
  }
};

// For internal uses
export const getDateTimeISOString = (dateString: string): string => {
  if (!dateString) {
    return "";
  }

  if (dateString.trim() == "") {
    return "";
  }

  try {
    const date = new Date(dateString);
    return date.toISOString().replace("T", " ").slice(0, 19) || ""; // YYYY-MM-DD HH:mm:ss
  } catch {
    return "";
  }
};
