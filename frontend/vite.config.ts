import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit(), devtoolsJson()],
  server: {
    // HMR doesn't really work as our websocket backend only handles a single connection
    // and dies when the connection closes (i.e. after frontend has the inital state)
    hmr: false,
  }
});
