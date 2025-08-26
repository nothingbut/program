// Tauri doesn't have a Node.js server to do proper SSR
// so we use adapter-static with a fallback to index.html to put the site in SPA mode
// See: https://svelte.dev/docs/kit/single-page-apps
// See: https://v2.tauri.app/start/frontend/sveltekit/ for more info
import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      fallback: "index.html",
    }),
  },
  compilerOptions: {
    warningFilter: (warning) => {
      // Suppress specific accessibility warnings for icon buttons
      if (warning.code === 'a11y_consider_explicit_label' && 
          warning.filename?.includes('PlayerControls.svelte')) {
        return false;
      }
      // Suppress click events warning for progress bar (it has proper keyboard support via role="slider")
      if (warning.code === 'a11y_click_events_have_key_events' && 
          warning.filename?.includes('PlayerControls.svelte')) {
        return false;
      }
      return true;
    }
  }
};

export default config;
