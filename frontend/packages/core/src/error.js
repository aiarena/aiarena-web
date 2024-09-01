export function handleServerError(error, description) {
    throw new Error(`${description}`);
  }