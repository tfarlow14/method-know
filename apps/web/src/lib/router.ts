import { writable } from 'svelte/store';

// Get initial location safely
function getInitialLocation(): string {
	if (typeof window === 'undefined') return '/';
	const hash = window.location.hash.slice(1);
	return hash || '/';
}

// Router store
export const location = writable(getInitialLocation());

// Initialize hash change listener
if (typeof window !== 'undefined') {
	// If pathname is not '/' and there's no hash, redirect to hash-based routing
	if (window.location.pathname !== '/' && !window.location.hash) {
		const path = window.location.pathname;
		window.location.replace(`/#${path}`);
	} else {
		// If there's no hash, set it to '/'
		if (!window.location.hash) {
			window.location.hash = '#/';
		}
		
		// Set initial location
		const initialLocation = getInitialLocation();
		location.set(initialLocation);
		
		// Listen for hash changes
		window.addEventListener('hashchange', () => {
			const newLocation = window.location.hash.slice(1) || '/';
			location.set(newLocation);
		});
	}
}

// Navigation functions
export function goto(path: string) {
	if (typeof window === 'undefined') return;
	const targetPath = path.startsWith('/') ? path : `/${path}`;
	// Ensure we're only setting the hash, not changing the pathname
	window.location.hash = `#${targetPath}`;
	location.set(targetPath);
}

export function replace(path: string) {
	if (typeof window === 'undefined') return;
	const targetPath = path.startsWith('/') ? path : `/${path}`;
	// Use replaceState to change hash without adding to history
	window.history.replaceState(null, '', `${window.location.pathname}#${targetPath}`);
	location.set(targetPath);
}
