import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit(), devtoolsJson()],
  server: {
    hmr: true,  // Set this to false to remove chance of HMR-related errors
  }
});
