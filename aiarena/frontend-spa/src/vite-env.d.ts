/// <reference types="vite/client" />

import type { reverseUrl } from "@/_lib/reverseUrl";

declare global {
  interface Window {
    BUILD_NUMBER: string;
    buildNumbersMismatch: boolean;
    Settings: {
      csrfToken: string;
    };
    // Exposed in main.tsx so the Playwright suite can assert it produces the same
    // paths as Django's `reverse` (the contract this helper upholds), and handy for
    // console debugging. Pure function over generated data — no state, no secrets.
    reverseUrl: typeof reverseUrl;
  }
}

export {};
