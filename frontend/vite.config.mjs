import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'REACT_APP_');
  return {
    plugins: [react()],
    // Keep the existing public API setting; never expose the entire environment.
    define: {
      'process.env.REACT_APP_API_URL': JSON.stringify(env.REACT_APP_API_URL || 'http://localhost:8000'),
    },
    build: { outDir: 'build', emptyOutDir: true },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/testSetup.js'],
    },
  };
});
