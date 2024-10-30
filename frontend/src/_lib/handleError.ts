interface ErrorInterface {
  message?: string;
  error?: any;
 
}

const handleError = (error: ErrorInterface): void => {
  console.error("An error occurred:", error);
  throw new Error (`An error occurred.`);
};

export default handleError;
