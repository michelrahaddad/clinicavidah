import { defineConfig } from 'vite';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
  },
});
