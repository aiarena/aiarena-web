import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import relay from 'vite-plugin-relay'
import path from 'path';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? 'https://static.aiarena.net/' : '/static/',
  plugins: [
    react(),
    relay,
  ],
  server: {
    host: 'localhost',
    origin: 'http://localhost:4000',
    port: 4000,
    open: false,
  },
  build: {
    manifest: true,
    emptyOutDir: true,
    outDir: path.resolve(__dirname, './static/dist'),
    rollupOptions: {
      input: ['./src/main.tsx'],
      cache: false,
      output: {
        sourcemap: true,
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          return null;
        },
      },
    },
  },
}));
