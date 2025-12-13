import { getAuthToken, clearAuthToken } from '$lib/auth';
import { goto } from '$lib/router';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ApiError {
	detail: string;
}

/**
 * API client for making requests to the backend
 */
export async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const token = getAuthToken();
	const url = `${API_BASE_URL}${endpoint}`;

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string> || {})
	};

	if (token) {
		// Ensure token is trimmed and properly formatted
		const cleanToken = token.trim();
		if (cleanToken) {
			headers['Authorization'] = `Bearer ${cleanToken}`;
		}
	}

	const response = await fetch(url, {
		...options,
		headers
	});

	if (!response.ok) {
		// Handle expired/invalid token (401 Unauthorized)
		if (response.status === 401) {
			// Don't redirect if we're already on the login page or if this is a login request
			const currentPath = typeof window !== 'undefined' 
				? window.location.hash.slice(1) || '/' 
				: '/';
			const isLoginPage = currentPath === '/login';
			const isLoginRequest = endpoint.includes('/login');
			
			if (!isLoginPage && !isLoginRequest) {
				clearAuthToken();
				goto('/login');
			}
		}

		const error: ApiError = await response.json().catch(() => ({
			detail: `HTTP error! status: ${response.status}`
		}));
		throw new Error(error.detail || 'An error occurred');
	}

	return response.json();
}

/**
 * GET request helper
 */
export function apiGet<T>(endpoint: string): Promise<T> {
	return apiRequest<T>(endpoint, { method: 'GET' });
}

/**
 * POST request helper
 */
export function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
	return apiRequest<T>(endpoint, {
		method: 'POST',
		body: data ? JSON.stringify(data) : undefined
	});
}

/**
 * PUT request helper
 */
export function apiPut<T>(endpoint: string, data?: unknown): Promise<T> {
	return apiRequest<T>(endpoint, {
		method: 'PUT',
		body: data ? JSON.stringify(data) : undefined
	});
}

/**
 * DELETE request helper
 */
export function apiDelete<T>(endpoint: string): Promise<T> {
	return apiRequest<T>(endpoint, { method: 'DELETE' });
}

