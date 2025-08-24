/// <reference types="vite/client" />

declare global {
  interface Window {
    BUILD_NUMBER: string;
    buildNumbersMismatch: boolean;
    Settings: {
      csrfToken: string;
    };
  }
}

export {};