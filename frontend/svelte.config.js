import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @typedef {import('svelte/compiler').Warning} Warning */

/** @type {import('@sveltejs/vite-plugin-svelte').SvelteConfig['onwarn']} */
const onwarn = function onwarn(/**@type {Warning}*/warning, /**@type {(Warning) => void}*/defaultHandler) {
  // I will put my styles next to the relevant HTML (ButtonDiv needs some way of 
  // receiveing styles and that way is currently class attribute + :global)
  if(warning.code == 'vite-plugin-svelte-css-no-scopable-elements') return;
  defaultHandler(warning);
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    // adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
    // If your environment is not supported, or you settled on a specific environment, switch out the adapter.
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter()
  },

  onwarn
};

export default config;
