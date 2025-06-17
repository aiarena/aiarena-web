import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./globals.css";
import App from "./App.tsx";
import { BrowserRouter } from "react-router";
import { RelayEnvironmentProvider } from "react-relay";
import environment from "@/_lib/RelayEnvironment";
import { SnackbarProvider } from "notistack";
import { RelayConnectionIDProvider } from "./_components/_contexts/RelayConnectionIDContext/RelayConnectionIDContext.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RelayEnvironmentProvider environment={environment}>
      <RelayConnectionIDProvider>
        <BrowserRouter>
          <SnackbarProvider>
            <App />
          </SnackbarProvider>
        </BrowserRouter>
      </RelayConnectionIDProvider>
    </RelayEnvironmentProvider>
  </StrictMode>
);
