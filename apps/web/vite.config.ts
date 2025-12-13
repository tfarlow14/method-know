import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
	plugins: [svelte()],
	resolve: {
		alias: {
			$lib: path.resolve('./src/lib')
		}
	},
	server: {
		// Ensure all routes fall back to index.html for hash-based routing
		fs: {
			allow: ['..']
		}
	},
	build: {
		rollupOptions: {
			input: {
				main: path.resolve(__dirname, 'index.html')
			}
		}
	}
});
