/**
 * Authentication utilities
 * 
 * Note: For production, consider using HttpOnly cookies instead of localStorage
 * for better security against XSS attacks.
 * 
 * User information is stored in Svelte stores (see stores.ts), not localStorage.
 * Only the authentication token is stored in localStorage.
 */

const AUTH_TOKEN_KEY = 'authToken';

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
	if (typeof window === 'undefined') {
		return false;
	}
	return !!localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Store authentication token (user info should be stored in Svelte store)
 */
export function setAuthToken(token: string): void {
	if (typeof window !== 'undefined') {
		// Trim whitespace before storing
		localStorage.setItem(AUTH_TOKEN_KEY, token.trim());
	}
}

/**
 * Get authentication token
 */
export function getAuthToken(): string | null {
	if (typeof window === 'undefined') {
		return null;
	}
	const token = localStorage.getItem(AUTH_TOKEN_KEY);
	// Trim whitespace in case it was accidentally added
	return token ? token.trim() : null;
}

/**
 * Remove authentication token (logout)
 * Note: User store should also be cleared when calling this
 */
export function clearAuthToken(): void {
	if (typeof window !== 'undefined') {
		localStorage.removeItem(AUTH_TOKEN_KEY);
	}
}

