import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./globals.css";
import App from "./App.tsx";
import { RelayEnvironmentProvider } from "react-relay";
import environment from "@/_lib/RelayEnvironment";
import { SnackbarProvider } from "notistack";
import { RelayConnectionIDProvider } from "./_components/_contexts/RelayConnectionIDContext/RelayConnectionIDContext.tsx";
import { SmartRouter } from "./SmartRouter.tsx";
import AlwaysScrollToTop from "./_lib/AlwaysScrollToTop.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <SnackbarProvider>
      <RelayEnvironmentProvider environment={environment}>
        <RelayConnectionIDProvider>
          <SmartRouter>
            <AlwaysScrollToTop />
            <App />
          </SmartRouter>
        </RelayConnectionIDProvider>
      </RelayEnvironmentProvider>
    </SnackbarProvider>
  </StrictMode>,
);
