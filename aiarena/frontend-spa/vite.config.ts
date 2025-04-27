import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import relay from "vite-plugin-relay";
import path from "path";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "https://aiarena.net/static/" : "/static/",
  plugins: [react(), tailwindcss(), relay],
  server: {
    host: "localhost",
    origin: "http://localhost:4000",
    port: 4000,
    open: false,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    manifest: true,
    sourcemap: true,
    emptyOutDir: true,
    outDir: path.resolve(__dirname, "./static/dist"),
    rollupOptions: {
      input: ["./src/main.tsx"],
      cache: false,
      output: {
        manualChunks: (id) => {
          if (id.includes("node_modules")) {
            return "vendor";
          }
          return null;
        },
      },
    },
  },
}));
